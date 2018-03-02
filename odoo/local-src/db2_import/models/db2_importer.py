# -*: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import os
import pyodbc
import socket
from datetime import datetime, timedelta
from calendar import monthrange

from odoo import api, fields, models
from odoo.addons.queue_job.job import job

import logging

_logger = logging.getLogger(__name__)


def convert_date(prefix, db2_row):
    dd = db2_row[prefix + 'jj']
    if dd == 0:
        return False
    mm = db2_row[prefix + 'mm']
    Y = "%s%02i" % (db2_row[prefix + 'ss'], db2_row[prefix + 'aa'])
    return "%s-%02i-%02i" % (Y, mm, dd)


def convert_customer(ref):
    return '__import__.customer_%s' % (ref)


def convert_supplier(ref):
    return '__import__.supplier_%s' % (ref)


def add_xmlid(record, xmlid, noupdate=False):
    """ Add a XMLID on an existing record """
    try:
        ref_id, __, __ = record.env['ir.model.data'].xmlid_lookup(xmlid)
    except ValueError:
        pass  # does not exist, we'll create a new one
    else:
        return record.env['ir.model.data'].browse(ref_id)
    if '.' in xmlid:
        module, name = xmlid.split('.')
    else:
        module = ''
        name = xmlid
    return record.env['ir.model.data'].create({
        'name': name,
        'module': module,
        'model': record._name,
        'res_id': record.id,
        'noupdate': noupdate,
    })


def create_or_update(model, xmlid, values):
    """ Create or update a record matching xmlid with values """
    record = model.env.ref(xmlid, raise_if_not_found=False)
    if record:
        record.update(values)
    else:
        record = model.create(values)
        add_xmlid(record, xmlid)
    return record


def convert_product_id(product_code):
    if product_code:
        xmlid = '__import__.product_%s' % product_code
    else:
        xmlid = '__setup__.product_other'
    return xmlid


def convert_user(resp_num):
    """ return user xmlid from a responsible number """
    if resp_num in (8, 9, 10):
        return False
    xmlid = '__setup__.res_user_%s' % resp_num
    return xmlid


def convert_coding(value):
    """Convert to utf8 and strip all DB2 messy strings"""
    if isinstance(value, basestring):
        value = value.decode('latin1').encode('utf8').strip()
    return value


def do_partial_picking(pick, lines, lots):
    """ Do a partial picking using delivered qty from DB2 """
    pick.action_confirm()
    pick.force_assign()
    pick.do_prepare_partial()
    for line in lines:
        product_xmlid = convert_product_id(line['dccart'])
        product = pick.env.ref(product_xmlid)
        ope = pick.pack_operation_ids.filtered(
            lambda p: p.product_id == product)
        if not ope:
            continue
        # += to make sure than we process all qty if there are
        # more than one line with same product
        ope.qty_done += line['dccqul']

        # pack operation requires serial num / lot
        if (ope.qty_done and ope.product_id and
                ope.product_id.tracking != 'none'):
            # there can be multiple lot for one product
            for db2_lot in lots:
                if (line['dccnli'] == db2_lot['mltnli'] and
                        line['dccart'] == db2_lot['mltart']):
                    odoo_lot = pick.env['stock.production.lot'].search(
                        [('name', '=', db2_lot['mltlot']),
                         ('product_id', '=', ope.product_id.id)])
                    OpeLot = pick.env['stock.pack.operation.lot']
                    values = {
                        'operation_id': ope.id,
                        'qty': -db2_lot['mltquc'],
                    }
                    if odoo_lot:
                        values['lot_id'] = odoo_lot.id
                    else:
                        values['lot_name'] = db2_lot['mltlot']
                    OpeLot.create(values)

    # in our case 0 on each operation means we don't want to transfer
    # as oposited to odoo process
    if any([op.qty_done for op in pick.pack_operation_ids]):
        pick.do_new_transfer()


def do_final_picking(pick, lines, lots):
    """ Transfert the last picking operations and lots are ok
    we need still to set quantities
    """
    for line in lines:
        product_xmlid = convert_product_id(line['dccart'])
        product = pick.env.ref(product_xmlid)
        ope = pick.pack_operation_ids.filtered(
            lambda p: p.product_id == product)
        if not ope:
            continue
        # += to make sure than we process all qty if there are
        # more than one line with same product
        ope.qty_done += line['dccqul']

        # pack operation requires serial num / lot
        if (ope.qty_done and ope.product_id and
                ope.product_id.tracking != 'none'):
            for db2_lot in lots:
                if (line['dccnli'] == db2_lot['mltnli'] and
                        line['dccart'] == db2_lot['mltart']):
                    for pack_lot in ope.pack_lot_ids:
                        if pack_lot.lot_id.name == db2_lot['mltlot']:
                            pack_lot.qty = -db2_lot['mltquc']
                            break
    # in our case 0 on each operation means we don't want to transfer
    # as oposited to odoo process
    if any([op.qty_done for op in pick.pack_operation_ids]):
        pick.do_new_transfer()


class DB2MapperPurchaseOrder(object):

    @classmethod
    def process(cls, rec, db2_table, tmp_id):
        cr = rec.env.cr
        query = (
            "SELECT id, ecfsui, ecfrin, ecfrcl, ecfuti, ecffou, ecfsuc,"
            "       ecfdjj, ecfdmm, ecfdaa, ecfdss,"
            "       ecfcjj, ecfcmm, ecfcaa, ecfcss,"
            "       ecfmjj, ecfmmm, ecfmaa, ecfmss"
            " FROM db2_pentcdfo WHERE id = %s")
        cr.execute(query, [tmp_id])
        row = cr.fetchone()
        if not row:
            raise Exception("Nothing to process")
        row = {c.lower(): row[idx]
               for idx, c in enumerate(
                   [d[0] for d in cr.description]
               )}

        create_date = convert_date('ecfc', row)
        supplier = rec.env.ref(convert_supplier(int(row['ecffou'])))
        promo_purchase = supplier.supplier_promotion_purchase_allowed

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
            'supplier_promotion_allowed': promo_purchase,
        }

        # transform float and string to int to remove . and spaces
        # while creating xmlid
        xmlid = '__import__.purchase_order_%s_%s_%s' % (
            row['ecfsui'], int(row['ecffou']), int(row['ecfsuc']))
        purchase_model = rec.env['purchase.order'].with_context(
            tracking_disable=True
        )
        new = create_or_update(
            purchase_model, xmlid, values)

        query = (
            "SELECT dcfart, dcfnli, dcflib, dcfquc, dcfqul, dcfpac, dcfrem,"
            "       dcfcjj, dcfcmm, dcfcaa, dcfcss,"
            "       dcfmjj, dcfmmm, dcfmaa, dcfmss"
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
            tracking_disable=True
        )
        po_lines = POLine
        is_received = True
        received_lines = []

        for line in lines:
            product_xmlid = convert_product_id(line['dcfart'])
            name = None
            if product_xmlid == '__setup__.product_other':
                name = "Divers"
            product = rec.env.ref(product_xmlid)
            create_date = convert_date('dcfc', line)
            taxes = product.supplier_taxes_id.filtered(
                lambda r: r.company_id == rec.env.user.company_id)
            values = {
                'order_id': new.id,
                'product_id': product.id,
                'sequence': line['dcfnli'],
                'name': name or line['dcflib'],
                'product_qty': line['dcfquc'],
                'product_uom': rec.env.ref('product.product_uom_unit').id,
                'qty_received': line['dcfqul'],
                'price_unit': line['dcfpac'],
                'discount_global': line['dcfres'],
                'promotion_supplier': line['dcfrem'],
                'date_planned': create_date,
                'create_date': create_date,
                'write_date': convert_date('dcfm', line) or create_date,
                'taxes_id': [(4, tax.id) for tax in taxes],
            }

            xmlid = '__import__.purchase_order_line_%s_%s_%s_%s' % (
                row['ecfsui'], int(row['ecffou']),
                int(row['ecfsuc']), int(line['dcfnli']))
            po_lines |= create_or_update(POLine, xmlid, values)
            received_lines.append(line['dcfquc'] <= line['dcfqul'])
        is_received = all(received_lines)

        if is_received:

            # validate purchase order
            new.write({
                'state': 'done',
            })
            # force received qty in database to avoid to have
            # to create pickings, this needs to be done after state write
            # or it would be recomputed
            query = (
                "UPDATE purchase_order_line"
                " SET qty_received = product_qty,"
                "     qty_invoiced = product_qty"
                " WHERE id in ( %s )"
            ) % ','.join(['%s'] * len(po_lines))
            cr.execute(query, po_lines.ids)
        else:
            new.write({
                'state': 'purchase',
            })


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

        create_date = convert_date('eccc', row)
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
            'fiscal_position_id': fpos.id,
            'supplier_promotion_allowed': promo_sale,
        }

        # transform float and string to int to remove . and spaces
        # while creating xmlid
        xmlid = '__import__.sale_order_%s_%s_%s' % (
            row['eccsui'], int(row['ecccli']), int(row['eccsuc']))
        so_model = rec.env['sale.order'].with_context(tracking_disable=True)
        new = create_or_update(so_model, xmlid, values)

        query = (
            "SELECT dccart, dccnli, dcclib, dccquc, dccqul, dccpvd, dccrem,"
            "       dcccjj, dcccmm, dcccaa, dcccss,"
            "       dccmjj, dccmmm, dccmaa, dccmss"
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
        SOLine = rec.env['sale.order.line'].with_context(tracking_disable=True)
        so_lines = SOLine
        is_delivered = True
        delivered_lines = []
        not_delivered_lines = []

        previous_line = None
        for line in lines:
            if line['dccart'].startswith('8888'):
                if not previous_line:
                    raise Exception(
                        "Cannot assign contribution tax on sale order %s\n"
                        " Tax cannot be the first line as we want to assign it"
                        " to previous line" % new.name)
                # For tax lines add them as tax to previous line
                cls.add_contrib_tax(rec, line, previous_line)
                continue
            product_xmlid = convert_product_id(line['dccart'])
            name = None
            if product_xmlid == '__setup__.product_other':
                name = "Divers"
            product = rec.env.ref(product_xmlid)
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
                'name': name or line['dcclib'],
                'product_uom_qty': line['dccquc'],
                'product_uom': rec.env.ref('product.product_uom_unit').id,
                'qty_delivered': line['dccqul'],
                'price_unit': line['dccpvd'],
                'tax_id': [(4, tax.id) for tax in taxes],
                'discount': line['dccrem'],
                'create_date': create_date,
                'write_date': convert_date('dccm', line) or create_date,
            }

            xmlid = '__import__.sale_order_line_%s_%s_%s_%s' % (
                row['eccsui'], int(row['ecccli']),
                int(row['eccsuc']), int(line['dccnli']))
            so_line = create_or_update(SOLine, xmlid, values)
            so_lines |= so_line
            previous_line = so_line
            delivered_lines.append(line['dccquc'] <= line['dccqul'])
            not_delivered_lines.append(line['dccqul'] == 0)
        is_delivered = all(delivered_lines)
        # don't do partial delivery when:
        # - everything is delivered (put the pick to done)
        # - delivery has not been started (keep picking in draft)
        is_partially_delivered = (
            not is_delivered and
            not all(not_delivered_lines)
        )

        if is_delivered:
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
            query = (
                "UPDATE sale_order_line"
                " SET qty_delivered = product_uom_qty,"
                "     qty_invoiced = product_uom_qty"
                " WHERE id in ( %s )"
            ) % ','.join(['%s'] * len(so_lines))
            cr.execute(query, so_lines.ids)
        elif rec.importer_id.mode == 'final_update':
            # This will need to be handled by hand if it was confirmed
            # by hand
            if new.state != 'draft':
                raise Exception(
                    "Cannot do final update for sale order %s"
                    " as not in draft state" % new.name)
            # Confirm the sale order to create the picking
            new.action_confirm()
            if is_partially_delivered:
                # Validate partially the pickings creating backorders
                picks = new.picking_ids
                loc_output = rec.env.ref('stock.stock_location_output')
                loc_customers = rec.env.ref('stock.stock_location_customers')
                picks1 = picks.filtered(
                    lambda p: p.location_dest_id == loc_output)
                pick2 = picks.filtered(
                    lambda p: p.location_dest_id == loc_customers)
                query = (
                    "SELECT mltlot, mltart, mltnli, mltquc"
                    " FROM db2_mvtlot"
                    " WHERE mltsui = %s"
                    " AND mltnum = %s"
                    " AND TRIM(mltsuc) = '%s'")
                cr.execute(
                    query,
                    (row['eccsui'], int(row['ecccli']),
                     int(row['eccsuc'])))
                lots = cr.fetchall()
                lots = [{c.lower(): lot[idx]
                         for idx, c in enumerate(
                            [d[0] for d in cr.description]
                         )} for lot in lots]
                # Do internal picking to out location
                for pick in picks1:
                    do_partial_picking(pick, lines, lots)
                # Do the deliver to customer
                do_final_picking(pick2, lines, lots)


mappers = {
    'PENTCDFO': DB2MapperPurchaseOrder,
    'PENTCDCL': DB2MapperSaleOrder,
}


class DB2ImporterTable(models.Model):
    _name = 'db2.importer.table'

    _PREFIX = 'db2_'

    schema = fields.Char(required=True)
    table_name = fields.Char(required=True)
    table_prefix = fields.Char(
        help="3 firsts character on each db2 column")
    id_columns = fields.Char(required=True)

    last_import = fields.Date()

    importer_id = fields.Many2one('db2.importer')
    create_job = fields.Boolean()
    eta = fields.Integer(
        default=2,
        help="Hour of the day when the db2 object will transformed to an odoo"
             " object")
    where_clause = fields.Char()

    @api.multi
    def get_add_columns(self):
        if self.table_name == 'PDETCDCL':
            # create a field on object table to manage relation
            return ', order_id integer references db2_pentcdcl(id)'
        elif self.table_name == 'PDETCDFO':
            # create a field on object table to manage relation
            return ', order_id integer references db2_pentcdfo(id)'
        return ''

    @api.multi
    def _get_db2_columns(self, db2_cr):
        """ Returns string containing definition of columns """
        query = (
            "SELECT column_name, data_type FROM qsys2.syscolumns"
            " WHERE table_schema = '{schema}'"
            " AND table_name = '{table_name}'".format(
                schema=self.schema,
                table_name=self.table_name))
        db2_cr.execute(query)
        columns = db2_cr.fetchall()
        type_mapping = {
            'NUMERIC': 'INTEGER',
            'CHAR': 'VARCHAR',
            'DECIMAL': 'DOUBLE PRECISION',
        }
        _logger.debug('GET COLUMNS FROM DB2 %s', columns)
        return ",".join(["{} {}".format(col[0], type_mapping[col[1]])
                         for col in columns])

    @api.multi
    def _create_db2_table(self, db2_columns):
        cr = self.env.cr
        odoo_table_name = self._PREFIX + self.table_name.lower()
        add_columns = self.get_add_columns()
        query = (
            "CREATE TABLE {} ("
            "id serial PRIMARY KEY,"
            "{}"
            "{}"
            ",UNIQUE({})"
            ")".format(odoo_table_name, db2_columns,
                       add_columns, self.id_columns))
        cr.execute(query)
        _logger.info('CREATE TABLE %s', odoo_table_name)

    def get_sql_query(self, date_start, date_end, col_names):

        query_kwargs = {
            'schema': self.schema,
            'table_name': self.table_name,
            'prefix': self.table_prefix,
        }

        if not date_start:
            date_start = self.last_import or "2017-01-01"
        query_kwargs.update({
            'start_age': int(date_start[:2]),
            'start_year': int(date_start[2:4]),
            'start_month': int(date_start[5:7]),
            'start_day': int(date_start[8:]),
        })
        if not date_end:
            start = fields.Date.from_string(date_start)
            start += timedelta(days=1)
            date_end = fields.Date.to_string(start)

        query_kwargs.update({
            'end_age': int(date_end[:2]),
            'end_year': int(date_end[2:4]),
            'end_month': int(date_end[5:7]),
            'end_day': int(date_end[8:]),
        })

        if '{}css'.format(self.table_prefix) in col_names:
            query = (
                "SELECT * FROM {schema}.{table_name}"
                " WHERE ({prefix}css >= {start_age}"
                " AND {prefix}css <= {end_age}"
                " AND {prefix}caa >= {start_year}"
                " AND {prefix}caa <= {end_year}"
                " AND {prefix}cmm >= {start_month}"
                " AND {prefix}cmm <= {end_month}"
                " AND {prefix}cjj >= {start_day}"
                " AND {prefix}cjj <= {end_day}"
            )

            if self.importer_id.mode == 'final_update':
                query += (
                    " OR {prefix}mss >= {start_age}"
                    " AND {prefix}mss <= {end_age}"
                    " AND {prefix}maa >= {start_year}"
                    " AND {prefix}maa <= {end_year}"
                    " AND {prefix}mmm >= {start_month}"
                    " AND {prefix}mmm <= {end_month}"
                    " AND {prefix}mjj >= {start_day}"
                    " AND {prefix}mjj <= {end_day})"
                )
            else:
                query += ")"
        else:
            query = (
                "SELECT * FROM {schema}.{table_name}"
                " WHERE {prefix}dss >= {start_age}"
                " AND {prefix}dss <= {end_age}"
                " AND {prefix}daa >= {start_year}"
                " AND {prefix}daa <= {end_year}"
                " AND {prefix}dmm >= {start_month}"
                " AND {prefix}dmm <= {end_month}"
                " AND {prefix}djj >= {start_day}"
                " AND {prefix}djj <= {end_day}"
            )
        if self.where_clause:
            query += " AND " + self.where_clause
        return query.format(**query_kwargs)

    def _setup_relations(self):
        cr = self.env.cr
        odoo_table_name = self._PREFIX + self.table_name.lower()
        if self.table_name == 'PDETCDCL':
            # assign foreign key on order_id when not set
            query = (
                "SELECT id, dccsui, dccncl, dccsuc"
                " FROM {} WHERE order_id IS NULL"
                ).format(odoo_table_name)
            cr.execute(query)
            rows = cr.fetchall()
            for row in rows:
                line_id = row[0]
                query = (
                    "SELECT id FROM db2_pentcdcl"
                    " WHERE eccsui = %s"
                    " AND ecccli = %s"
                    " AND eccsuc = %s"
                    )
                cr.execute(query, (row[1], row[2], row[3]))
                order_id = cr.fetchone()
                if order_id:
                    order_id = order_id[0]
                    query = "UPDATE {} SET order_id = %s WHERE id = %s".format(
                        odoo_table_name)
                    cr.execute(query, (order_id, line_id))
        elif self.table_name == 'PDETCDFO':
            # assign foreign key on order_id when not set
            query = (
                "SELECT id, dcfsui, dcffou, dcfsuc"
                " FROM {} WHERE order_id IS NULL"
                ).format(odoo_table_name)
            cr.execute(query)
            rows = cr.fetchall()
            for row in rows:
                line_id = row[0]
                query = (
                    "SELECT id FROM db2_pentcdfo"
                    " WHERE ecfsui = %s"
                    " AND ecffou = %s"
                    " AND ecfsuc = %s"
                    )
                cr.execute(query, (row[1], row[2], row[3]))
                order_id = cr.fetchone()
                if order_id:
                    order_id = order_id[0]
                    query = "UPDATE {} SET order_id = %s WHERE id = %s".format(
                        odoo_table_name)
                    cr.execute(query, (order_id, line_id))

    @api.multi
    @job(default_channel='root.db2.create_or_update')
    def create_or_update_record(self, db2_id):
        mappers[self.table_name].process(self, self.table_name, db2_id)

    @api.multi
    @job(default_channel='root.db2.fetch')
    def get_from_db2(self, date_start, date_end):
        # connect to DB2
        db2_host = os.environ.get('DB2HOST')
        if db2_host == 'pissh':
            # if DB2HOST is 'pissh' we use the container to
            # tunnel to internal network
            # We can't use DNS name in the DB2 odbc driver
            # thus we need to get the ip
            db2_host = socket.gethostbyname('pissh')
        db_user = os.environ.get('DB2USER')
        if not db_user:
            raise Exception("Env var DB2USER is not set")
        db_pwd = os.environ.get('DB2PWD')
        if not db_pwd:
            raise Exception("Env var DB2PWD is not set")
        conn = pyodbc.connect(
            "DSN=Alcyon", system=db2_host,
            uid=db_user, pwd=db_pwd)
        try:
            db2_cr = conn.cursor()
            cr = self.env.cr
            odoo_table_name = self._PREFIX + self.table_name.lower()
            cr.execute(
                "SELECT 1 FROM information_schema.tables"
                " WHERE table_name = '{}'".format(odoo_table_name))
            table_exists = cr.fetchone()

            if not table_exists:
                db2_columns = self._get_db2_columns(db2_cr)
                self._create_db2_table(db2_columns)
            # get all columns (from local copy)
            query = (
                "SELECT column_name"
                " FROM information_schema.columns"
                " WHERE table_name='{}'").format(odoo_table_name)
            cr.execute(query)
            cols = cr.fetchall()
            col_names = [col[0] for col in cols]
            if not self.table_prefix:
                for col in col_names:
                    if col != 'id':
                        self.table_prefix = col[:3].lower()
                        break
            query = self.get_sql_query(date_start, date_end, col_names)
            db2_cr.execute(query, [])

            rows = db2_cr.fetchall()
        finally:
            conn.close()
        if not rows:
            raise Exception("No data found please check your date range")

        # Save them locally
        columns = rows[0].cursor_description
        column_names = ",".join([col[0] for col in columns])

        query = (
            "INSERT INTO {table_name} ({column_names})"
            " VALUES ({placeholders})"
            " ON CONFLICT ({id_columns}) DO UPDATE"
            " SET {update_cols}"
            " RETURNING id"
        ).format(column_names=column_names,
                 id_columns=self.id_columns,
                 table_name=odoo_table_name,
                 placeholders=','.join(['%s']*len(columns)),
                 update_cols=','.join([col[0] + ' = %s' for col in columns]))
        eta = max(0, min(self.eta or 2, 23))
        now = datetime.now()
        next_eta = now.replace(hour=eta, minute=0, second=0, microsecond=0)
        # make sure the next eta is in future
        if next_eta < now:
            next_eta += timedelta(days=1)
        cpt = 0
        for row in rows:
            # Make list of values (x2) for insert and update placeholders
            values = [convert_coding(v) for v in row] * 2
            # Using mogrify to transform DECIMAL in int
            cr.execute(cr.mogrify(query, values))
            new_id = cr.fetchone()[0]
            cpt += 1
            if cpt % 10 == 0 or cpt == len(rows):
                _logger.info(
                    'INSERT %s %s on %s', self.table_name, cpt, len(rows))

            if self.create_job:
                # Prepare a job to execute the creation
                method_name = 'create_or_update_record'
                model = repr(self)
                func_string = "%s.%s(%s)" % (model, method_name, new_id)
                count_job = self.env['queue.job'].search_count(
                    [('model_name', '=', 'db2.importer.table'),
                     ('func_string', '=', func_string),
                     ('state', '!=', 'done')])
                if count_job:
                    continue
                self.with_delay(eta=next_eta).create_or_update_record(new_id)

        self._setup_relations()

        self.last_import = date_end


class DB2Importer(models.Model):
    _name = 'db2.importer'

    name = fields.Char()
    last_import = fields.Date()
    date_start = fields.Date()
    date_end = fields.Date()

    mode = fields.Selection([
        ('history', 'History'),
        ('final_update', 'Final update')],
        default='history')

    table_ids = fields.One2many('db2.importer.table', 'importer_id')

    @api.multi
    def db2_import(self):

        # split date range per month basis
        str_next_start = self.date_start
        dt_next_end = False
        dt_end = fields.Date.from_string(self.date_end)
        while not dt_next_end or dt_next_end < dt_end:
            dt_next_start = fields.Date.from_string(str_next_start)
            month_end = monthrange(dt_next_start.year, dt_next_start.month)[1]
            dt_next_end = min(dt_next_start.replace(day=month_end), dt_end)
            str_next_end = fields.Date.to_string(dt_next_end)
            # get data for each table
            for table in self.table_ids:
                table.with_delay().get_from_db2(str_next_start, str_next_end)
            str_next_start = fields.Date.to_string(
                dt_next_end + timedelta(days=1))
        self.last_import = fields.Datetime.now()
        self.date_start = self.last_import
        self.date_end = fields.datetime.now() + timedelta(days=10)
