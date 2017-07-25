# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import pyodbc
import socket
from datetime import datetime, timedelta

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


def do_partial_picking(pick, lines):
    """ Do a partial picking using delivered qty from DB2 """
    pick.action_confirm()
    pick.force_assign()
    for line in lines:
        product_xmlid = convert_product_id(line['dccart'])
        product = pick.env.ref(product_xmlid)
        ope = pick.pack_operation_pack_ids.filtered(
            lambda p: p.product_id == product)
        if not ope:
            continue
        # += to make sure than we process all qty if there are
        # more than one line with same product
        ope.qty_done += line['dccqul']
    # XXX don't validate because we don't have lot
    #pick.do_new_transfer()


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
        assert row, "Nothing to process"
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
        assert lines, "No lines were found"
        lines = [{c.lower(): convert_coding(line[idx])
                 for idx, c in enumerate(
                    [d[0] for d in cr.description]
                 )} for line in lines]
        is_delivered = True
        delivered_lines = []
        partial_delivered_lines = []

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

            SOLine = rec.env['sale.order.line'].with_context(
                create_original_line_too=True)
            xmlid = '__import__.sale_order_line_%s_%s_%s_%s' % (
                row['eccsui'], int(row['ecccli']),
                int(row['eccsuc']), int(line['dccnli']))
            create_or_update(SOLine, xmlid, values)
            delivered_lines.append(line['dccquc'] <= line['dccqul'])
            partial_delivered_lines.append(
                line['dccqul'] and line['dccquc'] > line['dccqul'])
        is_delivered = all(delivered_lines)
        is_partially_delivered = not any(partial_delivered_lines)

        if is_delivered:
            # validate sale order
            new.state = 'done'
        elif rec.importer_id.mode == 'final_update':
            # This will need to be handled by hand if it was confirmed
            # by hand
            assert new.state == 'draft'
            # Confirm the sale order to create the picking
            new.action_confirm()
            if is_partially_delivered:
                # Validate partially the pickings creating backorders
                picks = new.picking_ids
                for pick in picks.filtered(lambda p: p.state == 'confirmed'):
                    do_partial_picking(pick, lines)
                # XXX cannot confirm the second step as first step cannot
                # be validated without lots
                # pick2 = picks.filtered(lambda p: p.state == 'waiting')
                # do_partial_picking(pick2, lines)



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
            'CHAR': 'VARCHAR(50)',
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

    def get_sql_query(self, date_start, date_end):
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
        # TODO if
        DB2MapperSaleOrder.process(self, self.table_name, db2_id)

    def get_from_db2(self, db2_cr, date_start, date_end):
        cr = self.env.cr
        odoo_table_name = self._PREFIX + self.table_name.lower()
        cr.execute(
            "SELECT 1 FROM information_schema.tables"
            " WHERE table_name = '{}'".format(odoo_table_name))
        table_exists = cr.fetchone()

        if not table_exists:
            self._create_db2_table(db2_cr)
        if not self.table_prefix:
            query = (
                "SELECT column_name"
                " FROM information_schema.columns"
                " WHERE table_name='{}'").format(odoo_table_name)
            cr.execute(query)
            cols = cr.fetchall()
            for col in cols:
                col = col[0]
                if col != 'id':
                    self.table_prefix = col[:3].lower()
                    break
        query = self.get_sql_query(date_start, date_end)
        db2_cr.execute(query, [])

        rows = db2_cr.fetchall()
        if not rows:
            raise "No data found please check your date range"

        # Save them locally
        columns = rows[0].cursor_description
        column_names = ",".join([col[0] for col in columns])

        query = (
            u"INSERT INTO {table_name} ({column_names})"
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
        for row in rows:
            # Make list of values (x2) for insert and update placeholders
            values = [convert_coding(v) for v in row] * 2
            # Using mogrify to transform DECIMAL in int
            cr.execute(cr.mogrify(query, values))
            new_id = cr.fetchone()[0]
            _logger.info('INSERT 1 %s' % self.table_name)

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
        default='final_update')

    table_ids = fields.One2many('db2.importer.table', 'importer_id')

    @api.multi
    def db2_import(self):

        # connect to DB2
        # We can't use dns name in the DB2 odbc driver
        # thus we need to get the ip
        host = socket.gethostbyname('pissh')
        # TODO get db user and password from env var
        conn = pyodbc.connect(
            "DSN=Alcyon", system=host,
            uid=db_user, pwd=db_pwd)
        db2_cr = conn.cursor()

        # get data for each table
        for table in self.table_ids:
            table.get_from_db2(db2_cr, self.date_start, self.date_end)
        conn.close()
        self.last_import = fields.Datetime.now()
        self.date_start = self.last_import
        self.date_end = fields.datetime.now() + timedelta(days=10)
