# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime, timedelta

from .common import (
    convert_customer,
    convert_date,
    convert_product_id,
    convert_user,
    create_or_update,
    do_final_picking,
    do_partial_picking,
)


class DB2MapperSaleOrder(object):

    @classmethod
    def add_contrib_tax(cls, rec, tax_line, line):
        # check that quantity matches
        amount = tax_line['dccpvd']
        tax_domain = [
            ('type_tax_use', '=', 'sale'),
            ('amount', '=', amount),
            ('name', '=like', 'ANTIBIO%')]
        tax = rec.env['account.tax'].search(tax_domain)
        line.tax_id |= tax

    @classmethod
    def map_orderline2move(cls, lines):
        mapping = [
            ('product', 'dccart'),
            ('qty_done', 'dccqul'),
            ('line_no', 'dccnli'),
        ]
        pick_lines = [{src: l[dest] for src, dest in mapping} for l in lines]
        return pick_lines

    @classmethod
    def process(cls, rec, db2_table, tmp_id):
        cr = rec.env.cr
        query = (
            "SELECT id, eccsui, eccrin, eccrcl, eccrep, ecccli, eccsuc,"
            "       eccdjj, eccdmm, eccdaa, eccdss,"
            "       ecccjj, ecccmm, ecccaa, ecccss,"
            "       eccmjj, eccmmm, eccmaa, eccmss"
            " FROM db2_pentcdcl WHERE id = %s")
        cr.execute(query, [tmp_id])
        row = cr.fetchone()
        if not row:
            raise Exception("Nothing to process")
        row = {c.lower(): row[idx]
               for idx, c in enumerate(
                   [d[0] for d in cr.description]
               )}
        # transform float and string to int to remove . and spaces
        # while creating xmlid
        xmlid = '__import__.sale_order_%s_%s_%s' % (
            row['eccsui'], int(row['ecccli']), int(row['eccsuc']))
        sale = rec.env.ref(xmlid, raise_if_not_found=False)
        # Do not update an already done sale order
        if sale and sale.state == 'done':
            return

        create_date = convert_date('eccc', row)
        # a sale order becomes unactive after 120 days
        # (AS400 doesn't has a proper done state)
        date_120d_old = (datetime.today().date() - timedelta(days=120))
        date_120d_old = datetime.strftime(date_120d_old, "%Y-%m-%d")
        expired = create_date < date_120d_old
        customer = rec.env.ref(convert_customer(int(row['ecccli'])))
        pricelist = customer.property_product_pricelist
        pay_term = customer.property_payment_term_id
        addr = customer.address_get(['delivery', 'invoice'])

        delivery = rec.env['res.partner'].browse(addr['delivery'])
        # take fiscal posistion to work with a record
        # partner manually set fiscal position always win
        fpos = (delivery.property_account_position_id or
                customer.property_account_position_id)
        if not fpos:
            fp_obj = rec.env['account.fiscal.position']
            # First search only matching VAT positions
            vat_required = bool(customer.vat)
            fpos = fp_obj._get_fpos_by_region(
                delivery.country_id.id,
                delivery.state_id.id,
                delivery.zip,
                vat_required)

            # Then if VAT required found no match, try positions that do not
            # require it
            if not fpos and vat_required:
                fpos = fp_obj._get_fpos_by_region(
                    delivery.country_id.id,
                    delivery.state_id.id, delivery.zip, False)

        promo_sale = customer.supplier_promotion_sale_allowed

        user_xmlid = convert_user(row['eccrep'])
        values = {
            'name': row['eccsui'],
            'origin': row['eccrin'],
            'client_order_ref': row['eccrcl'],
            'user_id': user_xmlid and rec.env.ref(user_xmlid).id,
            'currency_id': rec.env.ref('base.EUR').id,
            'date_order': convert_date('eccd', row),
            'create_date': create_date,
            'confirmation_date': convert_date('eccd', row),
            'write_date': convert_date('eccm', row) or create_date,
            'partner_id': customer.id,
            'pricelist_id': pricelist.id,
            'payment_term_id': pay_term.id,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': delivery.id,
            'fiscal_position_id': fpos and fpos.id,
            'supplier_promotion_allowed': promo_sale,
            'ignore_exception': True,
        }

        so_model = rec.env['sale.order'].with_context(
            tracking_disable=True,
            no_connector_export=True,
        )
        new = create_or_update(so_model, xmlid, values)\
            .with_context(skip_pdf_gen=True)

        query = (
            "SELECT dccart, dccnli, dcclib, dccquc, dccqul, dccpvd, dccrem,"
            "       dccres,"
            "       dcccjj, dcccmm, dcccaa, dcccss,"
            "       dccmjj, dccmmm, dccmaa, dccmss,"
            "       dccsgr, dcccgr,"
            "       deleted"                          # deleted on AS400
            " FROM db2_pdetcdcl WHERE order_id = %s"
            " ORDER BY dccnli")
        cr.execute(query, [row['id']])

        lines = cr.fetchall()
        if not lines:
            raise Exception("No lines were found")
        lines = [{c.lower(): line[idx]
                 for idx, c in enumerate(
                    [d[0] for d in cr.description]
                 )} for line in lines]
        if any(l['dccquc'] < 0 for l in lines):
            raise Exception("Negative qty in lines")
        SOLine = rec.env['sale.order.line'].with_context(
            tracking_disable=True,
            no_connector_export=True,
        )
        so_lines = SOLine
        is_done = True
        delivered_lines = []
        not_delivered_lines = []
        expired_adjustments = []

        # register non skipped lines
        valid_lines = []
        deleted_lines = []
        previous_line = None
        for line in lines:
            if line['deleted']:
                deleted_lines.append(line)
                continue

            product_code = line['dccart']
            if not product_code:
                # skip lines without product reference
                # those lines are replaced products
                # we won't import replacements in history
                continue
            elif product_code.startswith('8888'):
                if not previous_line:
                    raise Exception(
                        "Cannot assign contribution tax on sale order %s\n"
                        " Tax cannot be the first line as we want to assign it"
                        " to previous line" % new.name)
                # For tax lines add them as tax to previous line
                cls.add_contrib_tax(rec, line, previous_line)
                continue
            product_xmlid = convert_product_id(product_code)
            product = rec.env.ref(product_xmlid)
            if line['dcccgr'] == 1 and line['dccsgr'] != 15:
                # Free accessory, in odoo are inserted in the picking
                # But check that it is not human (15) ?!
                if product.product_tmpl_id.is_an_additional_product():
                    # And if it is an accessory of another product, skip it
                    continue
            valid_lines.append(line)
            # While odoo could do it for us on create
            # in _prepare_add_missing_fields
            # Do it ourselves to avoid call to onchange
            taxes = product.taxes_id.filtered(
                lambda r: r.company_id == rec.env.user.company_id)
            taxes = fpos.map_tax(
                taxes, product, new.partner_shipping_id) if fpos else taxes
            create_date = convert_date('dccc', line)
            values = {
                'order_id': new.id,
                'product_id': product.id,
                'sequence': line['dccnli'],
                'name': line['dcclib'],
                'product_uom_qty': line['dccquc'],
                'product_uom': rec.env.ref('product.product_uom_unit').id,
                'qty_delivered': line['dccqul'],
                'price_unit': line['dccpvd'],
                'tax_id': [(4, tax.id) for tax in taxes],
                # discount field is hidden and replaced by
                # discount2 and discount3
                'discount': 0,
                'discount2': line['dccres'],
                'discount3': line['dccrem'],
                'create_date': create_date,
                'write_date': convert_date('dccm', line) or create_date,
            }

            xmlid = '__import__.sale_order_line_%s_%s_%s_%s' % (
                row['eccsui'], int(row['ecccli']),
                int(row['eccsuc']), int(line['dccnli']))
            so_line = create_or_update(SOLine, xmlid, values)
            so_lines |= so_line
            if expired and line['dccquc'] != line['dccqul']:
                expired_adjustments.append((so_line, line['dccqul']))
            previous_line = so_line
            delivered_lines.append(line['dccquc'] <= line['dccqul'])
            not_delivered_lines.append(line['dccqul'] == 0)

        # fully delivered order and orders older than 120 days are done
        is_done = all(delivered_lines) or expired

        # don't do partial delivery when:
        # - everything is delivered (put the pick to done)
        # - delivery has not been started (keep picking in draft)
        is_partially_delivered = (
            not is_done and
            not all(not_delivered_lines)
        )

        # check if we need to clean deleted lines
        for line in deleted_lines:
            xmlid = '__import__.sale_order_line_%s_%s_%s_%s' % (
                row['eccsui'], int(row['ecccli']),
                int(row['eccsuc']), int(line['dccnli']))
            line_rec = rec.env.ref(xmlid, raise_if_not_found=False)
            line_rec.unlink()

        if is_done:
            # validate sale order
            new.write({
                'state': 'done',
                'invoice_status': 'invoiced'
            })
            cr.execute(
                "UPDATE sale_order set invoice_status = 'invoiced'"
                " WHERE id = %s", [new.id])
            # force invoiced qty in database to avoid to have
            # this needs to be done after state write
            # or it would be recomputed

            sol_ids = so_lines.ids
            if expired_adjustments:
                for (sol, _) in expired_adjustments:
                    if sol.id in sol_ids:
                        sol_ids.remove(sol.id)

            if sol_ids:
                # main fast case: ordered = delivered
                query = (
                    "UPDATE sale_order_line"
                    " SET qty_delivered = product_uom_qty,"
                    "     qty_invoiced = product_uom_qty"
                    " WHERE id in ( %s )"
                ) % ','.join(['%s'] * len(sol_ids))
                cr.execute(query, sol_ids)
            if not expired_adjustments:
                # set delivered quantities for old orders we closed without
                # everything delivered
                for (sol, qty) in expired_adjustments:
                    query = (
                        "UPDATE sale_order_line"
                        " SET qty_delivered = %s,"
                        "     qty_invoiced = %s"
                        " WHERE id = %s"
                    )
                    cr.execute(query, sol.id, qty, qty)

        elif rec.importer_id.mode == 'final_update':
            # This will need to be handled by hand if it was confirmed
            # by hand
            if new.state != 'draft':
                raise Exception(
                    "Cannot do final update for sale order %s"
                    " as not in draft state" % new.name)
            # Confirm the sale order to create the picking
            new.with_context(
                skip_pdf_gen=True,  # disable specific_report pdf auto-gen
                nogrouppicking=True,  # disable stock_groupbypartner
                __no_promotional_product=True,  # disable add promo lines
                ).action_confirm()

            if is_partially_delivered:
                # Validate partially the pickings creating backorders
                picks = new.picking_ids
                loc_output = rec.env.ref('stock.stock_location_output')
                loc_customers = rec.env.ref('stock.stock_location_customers')
                picks1 = picks.filtered(
                    lambda p: p.location_dest_id == loc_output)
                pick2 = picks.filtered(
                    lambda p: p.location_dest_id == loc_customers)
                pick_lines = cls.map_orderline2move(valid_lines)
                # Do internal pickings to output location
                for pick in picks1:
                    do_partial_picking(pick, pick_lines)
                    # find backorder
                    bo = rec.env['stock.picking'].search(
                        [('backorder_id', '=', pick.id)])
                    if bo:
                        # make sure backorder is not assigned
                        bo.do_unreserve()
                # Do the deliver to customer
                do_final_picking(pick2, pick_lines)
                # find backorder
                bo = rec.env['stock.picking'].search(
                    [('backorder_id', '=', pick2.id)])
                if bo:
                    # make sure backorder is not assigned
                    bo.do_unreserve()

        return new
