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
    Y = "%s%s" % (db2_row[prefix + 'ss'], db2_row[prefix + 'aa'])
    return "%s-%02i-%02i" % (Y, mm, dd)


def convert_customer(ref):
    return '__import__.customer_%s' % (ref)


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

    product = (product_code or '').strip()
    if product:
        xmlid = '__import__.product_%s' % product
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
    if isinstance(value, str):
        value = value.decode('latin1').encode('utf8')
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
                        line['dccart'].strip() == db2_lot['mltart'].strip()):
                    odoo_lot = pick.env['stock.production.lot'].search(
                        [('name', '=', db2_lot['mltlot'].strip())])
                    OpeLot = pick.env['stock.pack.operation.lot']
                    values = {
                        'operation_id': ope.id,
                        'qty': -db2_lot['mltquc'],
                    }
                    if odoo_lot:
                        values['lot_id'] = odoo_lot.id
                    else:
                        values['lot_name'] = db2_lot['mltlot'].strip()
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
                        line['dccart'].strip() == db2_lot['mltart'].strip()):
                    for pack_lot in ope.pack_lot_ids:
                        if pack_lot.lot_id.name == db2_lot['mltlot'].strip():
                            pack_lot.qty = -db2_lot['mltquc']
                            break
    # in our case 0 on each operation means we don't want to transfer
    # as oposited to odoo process
    if any([op.qty_done for op in pick.pack_operation_ids]):
        pick.do_new_transfer()


class DB2MapperSaleOrder(object):

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
        row = {c.lower(): convert_coding(row[idx])
               for idx, c in enumerate(
                   [d[0] for d in cr.description]
               )}

        create_date = convert_date('eccc', row)

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
            'partner_id': rec.env.ref(convert_customer(int(row['ecccli']))).id,
        }

        # transform float and string to int to remove . and spaces
        # while creating xmlid
        xmlid = '__import__.sale_order_%s_%s_%s' % (
            row['eccsui'], int(row['ecccli']), int(row['eccsuc']))
        new = create_or_update(rec.env['sale.order'], xmlid.strip(), values)

        query = (
            "SELECT dccart, dccnli, dcclib, dccquc, dccqul, dccpvd, dccrem,"
            "       dcccjj, dcccmm, dcccaa, dcccss,"
            "       dccmjj, dccmmm, dccmaa, dccmss"
            " FROM db2_pdetcdcl WHERE order_id = %s")
        cr.execute(query, [row['id']])

        lines = cr.fetchall()
        if not lines:
            raise Exception("No lines were found")
        lines = [{c.lower(): convert_coding(line[idx])
                 for idx, c in enumerate(
                    [d[0] for d in cr.description]
                 )} for line in lines]
        is_delivered = True
        delivered_lines = []
        not_delivered_lines = []

        for line in lines:
            product_xmlid = convert_product_id(line['dccart'])
            name = None
            if product_xmlid == '__setup__.product_other':
                name = "Divers"
            product = rec.env.ref(product_xmlid)
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
                'discount': line['dccrem'],
                'create_date': create_date,
                'write_date': convert_date('dccm', line) or create_date,
            }

            SOLine = rec.env['sale.order.line']
            xmlid = '__import__.sale_order_line_%s_%s_%s_%s' % (
                row['eccsui'], int(row['ecccli']),
                int(row['eccsuc']), int(line['dccnli']))
            create_or_update(SOLine, xmlid, values)
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
                lots = [{c.lower(): convert_coding(lot[idx])
                         for idx, c in enumerate(
                            [d[0] for d in cr.description]
                         )} for lot in lots]
                # Do internal picking to out location
                for pick in picks1:
                    do_partial_picking(pick, lines, lots)
                # Do the deliver to customer
                do_final_picking(pick2, lines, lots)


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

    @api.multi
    def get_add_columns(self):
        if self.table_name == 'PDETCDCL':
            # create a field on object table to manage relation
            return ', order_id integer references db2_pentcdcl(id)'
        return ''

    @api.multi
    def _create_db2_table(self, db2_cr):
        cr = self.env.cr
        odoo_table_name = self._PREFIX + self.table_name.lower()
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
        columns = ",".join(["{} {}".format(col[0], type_mapping[col[1]])
                           for col in columns])

        add_columns = self.get_add_columns()

        query = (
            "CREATE TABLE {} ("
            "id serial PRIMARY KEY,"
            "{}"
            "{}"
            ",UNIQUE({})"
            ")".format(odoo_table_name, columns, add_columns, self.id_columns))
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
                " WHERE {prefix}css >= {start_age}"
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
                    " AND {prefix}mjj <= {end_day}"
                )
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

    @api.multi
    @job
    def create_or_update_record(self, db2_id):
        # TODO if in function of model
        DB2MapperSaleOrder.process(self, self.table_name, db2_id)

    @api.multi
    @job
    def get_from_db2(self, date_start, date_end):
        # connect to DB2
        # We can't use dns name in the DB2 odbc driver
        # thus we need to get the ip
        host = socket.gethostbyname('pissh')
        db_user = os.environ.get('DB2USER')
        if not db_user:
            raise Exception("Env var DB2USER is not set")
        db_pwd = os.environ.get('DB2PWD')
        if not db_pwd:
            raise Exception("Env var DB2PWD is not set")
        conn = pyodbc.connect(
            "DSN=Alcyon", system=host,
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
                self._create_db2_table(db2_cr)
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
                    'INSERT %s %s on %s' % (self.table_name, cpt, len(rows)))

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
