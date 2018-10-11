# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime, timedelta

from . import mappings
from .common import (
    convert_date,
    convert_product_id,
    convert_supplier,
    create_or_update,
    do_picking,
)


def create_supplier_invoice(order, lines):

    # nfa is a reference to an invoice qul is received qty
    invoiced_lines = [l for l in lines if l['dcfnfa'] and l['dcfqul'] > 0]
    if not invoiced_lines:
        return
    invoiced_lines_no = [l['dcfnli'] for l in invoiced_lines]

    journal_xid = '__setup__.account_journal_achat_migration'
    journal = order.env.ref(journal_xid)

    partner = order.partner_id
    pay_account = partner.property_account_payable_id
    payment_term = partner.property_supplier_payment_term_id
    delivery_partner_id = partner.address_get(['delivery'])['delivery']
    fp_id = order.env['account.fiscal.position'].get_fiscal_position(
        partner.id, delivery_id=delivery_partner_id)

    vals = {'name': '[MIGRATION] PO %s' % order.name,
            'date_invoice': order.date_order,
            'purchase_id': order.id,
            'type': 'in_invoice',
            'partner_id': partner.id,
            'journal_id': journal.id,
            'account_id': pay_account.id,
            'payment_term_id': payment_term.id,
            'fiscal_position_id': fp_id,
            }
    invoice = order.env['account.invoice'].create(vals)

    new_lines = order.env['account.invoice.line']
    for line in order.order_line:
        if line.sequence in invoiced_lines_no:
            data = invoice._prepare_invoice_line_from_po_line(line)
            data['price_unit'] = 0.0
            new_line = new_lines.create(data)
            new_line._set_additional_fields(invoice)
            new_lines += new_line
    invoice.invoice_line_ids = new_lines
    invoice.state = 'paid'


class DB2MapperPurchaseOrder(object):

    @classmethod
    def prepare_purchase_values(cls, rec, row):
        create_date = convert_date('ecfc', row)
        supplier = rec.env.ref(convert_supplier(int(row['ecffou'])))

        # FIXME Don't take user for now as we don't have related users
        # user_xmlid = convert_user(row['ecfuti'])
        values = {
            'name': row['ecfsui'],
            'origin': row['ecfrin'],
            'partner_ref': row['ecfrcl'],
            # 'user_id': user_xmlid and rec.env.ref(user_xmlid).id,
            'currency_id': rec.env.ref('base.EUR').id,
            'date_order': convert_date('ecfd', row),
            'create_date': create_date,
            'write_date': convert_date('ecfm', row) or create_date,
            'partner_id': supplier.id,
        }
        return values

    @classmethod
    def map_orderline2move(cls, lines):
        mapping = [
            ('product', 'dcfart', False),
            ('qty_done', 'dcfqul', False),
            ('line_no', 'dcfnli', False),
            ('date', 'dcfc', convert_date),
            ('date_expected', 'dcfl', convert_date),
        ]
        pick_lines = [{src: fct(dest, l) if fct else l[dest]
                       for src, dest, fct in mapping} for l in lines]
        return pick_lines

    @classmethod
    def process(cls, rec, db2_table, tmp_id):
        cr = rec.env.cr
        query = (
            "SELECT id, ecfsui, ecfrin, ecfrcl, ecfuti, ecffou, ecfsuc,"
            "       ecfdjj, ecfdmm, ecfdaa, ecfdss,"  # order date
            "       ecfcjj, ecfcmm, ecfcaa, ecfcss,"  # create date
            "       ecfmjj, ecfmmm, ecfmaa, ecfmss,"   # modification date
            "       ecfljj, ecflmm, ecflaa, ecflss"   # delivery date
            " FROM db2_pentcdfo WHERE id = %s")
        cr.execute(query, [tmp_id])
        row = cr.fetchone()
        if not row:
            raise Exception("Nothing to process")
        row = {c.lower(): row[idx]
               for idx, c in enumerate(
                   [d[0] for d in cr.description]
               )}
        values = cls.prepare_purchase_values(rec, row)

        # a sale order becomes unactive after 120 days
        # (AS400 doesn't has a proper done state)
        date_120d_old = (datetime.today().date() - timedelta(days=120))
        date_120d_old = datetime.strftime(date_120d_old, "%Y-%m-%d")
        create_date = convert_date('ecfc', row)
        expired = create_date < date_120d_old

        # transform float and string to int to remove . and spaces
        # while creating xmlid
        xmlid = '__import__.purchase_order_%s_%s_%s' % (
            row['ecfsui'], int(row['ecffou']), int(row['ecfsuc']))
        purchase = rec.env.ref(xmlid, raise_if_not_found=False)
        # Do not update an already done purchase order
        if purchase and purchase.state == 'done':
            return

        purchase_model = rec.env['purchase.order'].with_context(
            tracking_disable=True,
        )
        new = create_or_update(
            purchase_model, xmlid, values)

        # We need to set the purchase to draft before writing
        # its lines, otherwise it will automatically create pickings
        # when product_qty is written and purchase state is 'purchase'
        # in src/addons/purchase/models/purchase.py:610
        # this state is written again later
        new.write({
            'state': 'draft',
        })

        query = (
            "SELECT dcfart, dcfnli, dcflib, dcfquc, dcfqul, dcfpac, dcfrem,"
            "       dcfres, dcfunv, dcfnfa,"
            "       dcfcjj, dcfcmm, dcfcaa, dcfcss,"  # creation date
            "       dcfmjj, dcfmmm, dcfmaa, dcfmss,"  # modification date
            "       dcfljj, dcflmm, dcflaa, dcflss,"  # delivery date
            "       dcffjj, dcffmm, dcffaa, dcffss,"   # done date
            "       deleted"                          # deleted on AS400
            " FROM db2_pdetcdfo WHERE order_id = %s")
        cr.execute(query, [row['id']])

        lines = cr.fetchall()
        if not lines:
            raise Exception("No lines were found")
        lines = [{c.lower(): line[idx]
                 for idx, c in enumerate(
                    [d[0] for d in cr.description]
                 )} for line in lines]
        if any(l['dcfquc'] < 0 for l in lines):
            raise Exception("Negative qty in lines")
        POLine = rec.env['purchase.order.line'].with_context(
            tracking_disable=True,
        )
        po_lines = POLine
        is_received = True
        received_lines = []
        not_received_lines = []

        # skip lines without product reference
        # those lines are replaced products
        # we won't import replacements in history
        deleted_lines = [l for l in lines if l['deleted']]
        lines = [l for l in lines if l['dcfart'] and not l['deleted']]
        for line in lines:
            product_code = line['dcfart']
            product_xmlid = convert_product_id(product_code)
            product = rec.env.ref(product_xmlid)

            create_date = convert_date('dcfc', line)
            delivery_date = convert_date('dcfl', line)
            # If company_id is set, always filter taxes by the company
            taxes = product.supplier_taxes_id.filtered(
                lambda r: not new.company_id or r.company_id == new.company_id
            )
            fpos = (new.fiscal_position_id
                    or new.partner_id.property_account_position_id)
            taxes = (
                fpos.map_tax(
                    taxes, product, new.partner_id) if fpos
                else taxes)
            values = {
                'order_id': new.id,
                'product_id': product.id,
                'sequence': line['dcfnli'],
                'name': line['dcflib'],
                'product_qty': line['dcfquc'],
                'product_uom': rec.env.ref(mappings.UOM[line['dcfunv']]).id,
                'qty_received': line['dcfqul'],
                'price_unit': line['dcfpac'],
                'discount_global': line['dcfrem'],
                'promotion_supplier': line['dcfres'],
                'date_planned': delivery_date or create_date,
                'create_date': create_date,
                'write_date': convert_date('dcfm', line) or create_date,
                'taxes_id': [(4, tax.id) for tax in taxes],
            }

            xmlid = '__import__.purchase_order_line_%s_%s_%s_%s' % (
                row['ecfsui'], int(row['ecffou']),
                int(row['ecfsuc']), int(line['dcfnli']))
            line_rec = create_or_update(POLine, xmlid, values)
            line['odoo_id'] = line_rec.id
            po_lines |= line_rec
            received_lines.append(line['dcfquc'] <= line['dcfqul'])
            not_received_lines.append(line['dcfqul'] == 0)

        if deleted_lines:
            # temporarily change state to draft
            new.write({'state': 'draft'})
        # check if we need to clean deleted lines
        for line in deleted_lines:
            xmlid = '__import__.purchase_order_line_%s_%s_%s_%s' % (
                row['ecfsui'], int(row['ecffou']),
                int(row['ecfsuc']), int(line['dcfnli']))
            line_rec = rec.env.ref(xmlid, raise_if_not_found=False)
            if line_rec:
                line_rec.unlink()

        is_received = all(received_lines)
        is_done = is_received or expired
        # don't do partial delivery when:
        # - everything is received (put the pick to done)
        # - reception has not been started (keep picking in draft)
        is_partially_received = (
            not is_received and
            not all(not_received_lines)
        )

        state = 'done' if is_done else 'purchase'
        new.write({
            'state': state,
        })
        if is_done:
            # force invoiced and received qty in database to avoid to have
            # to create pickings, this needs to be done after state write
            # or it would be recomputed
            query = (
                "UPDATE purchase_order_line"
                " SET qty_invoiced = product_qty"
                " WHERE id in ( %s )"
            ) % ','.join(['%s'] * len(po_lines))
            cr.execute(query, po_lines.ids)
            query = (
                "UPDATE purchase_order_line"
                " SET qty_received = %s"
                " WHERE id = %s"
            )
            for line in lines:
                # dcfqul is delivered quantity
                cr.execute(query, (line['dcfqul'], line['odoo_id']))

        elif rec.importer_id.mode == 'final_update':
            new._create_picking()
            if is_partially_received:
                # if partially received create a backorder with
                # received quantities
                pick = new.picking_ids

                picking_date = convert_date('ecfc', row)
                scheduled_date = convert_date('ecfl', row)
                # as we do only one picking take the max date
                # from lines for receival dates
                date_done = max(convert_date('dcff', l) for l in lines)
                pick.write({
                    'date': picking_date,
                    'min_date': scheduled_date,
                    'date_done': date_done,
                })
                pick_lines = cls.map_orderline2move(lines)
                do_picking(pick, pick_lines)

                # find backorder
                bo = rec.env['stock.picking'].search(
                    [('backorder_id', '=', pick.id)])
                if bo:
                    # make sure backorder is not assigned
                    bo.do_unreserve()

                # create invoice for invoiced lines
                create_supplier_invoice(new, lines)
        return new
