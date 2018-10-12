# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import os
import pyodbc
import socket
import uuid
from datetime import datetime, timedelta
from calendar import monthrange

from odoo import api, fields, models
from odoo.addons.queue_job.job import job

from ..converter import sale, purchase, ticket
from ..converter.common import convert_coding

import logging

_logger = logging.getLogger(__name__)


mappers = {
    'PENTCDFO': purchase.DB2MapperPurchaseOrder,
    'PENTCDCL': sale.DB2MapperSaleOrder,
    'HISPRB': ticket.DB2MapperHelpdeskTicket,
}


class DB2ImporterTable(models.Model):
    _name = 'db2.importer.table'

    _PREFIX = 'db2_'

    schema = fields.Char(required=True)
    table_name = fields.Char(required=True)
    table_prefix = fields.Char(
        help="3 firsts character on each db2 column")
    id_columns = fields.Char(required=True)

    importer_id = fields.Many2one('db2.importer')
    create_job = fields.Boolean()
    eta = fields.Integer(
        default=2,
        help="Hour of the day when the db2 object will transformed to an odoo"
             " object")
    where_clause = fields.Char()
    csv_until = fields.Date(
        help="If a csv was injected into database, put here the lasted date of"
             " of its data.")

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

    def _get_sql_where_date(self, date_start, date_end, col_names=None):
        """In DB2 dates are splitted through 4 fields:
        - age (century)
        - year (2 digits)
        - month
        - day

        Here we construct a request by converting them in a single integer
        this operation is thus cross compatible in DB2 and psql.

        DRECEP table is an exception with a single date column containing
        an integer.

        """
        date_start = int(date_start.replace('-', ''))
        date_end = int(date_end.replace('-', ''))

        # Claims have no create or modification date
        # there is a single date in int format
        if self.table_name == 'DRECEP':
            return "drpdat >= %s AND drpdat <= %s" % (date_start, date_end)
        elif self.table_name == 'HISPRB':
            return "hpbdat >= %s AND hpbdat <= %s" % (date_start, date_end)
        elif self.table_name == 'HISSPR':
            return "hpsdat >= %s AND hpsdat <= %s" % (date_start, date_end)

        query_kwargs = {
            'prefix': self.table_prefix,
        }

        query_kwargs.update({
            'start_date': date_start
        })
        if not date_end:
            start = fields.Date.from_string(date_start)
            start += timedelta(days=1)
            date_end = fields.Date.to_string(start)

        query_kwargs.update({
            'end_date': date_end,
        })

        if not col_names or '{}css'.format(self.table_prefix) in col_names:
            where = (
                " ("
                "  {prefix}css * 1000000 +"
                "  {prefix}caa * 10000 +"
                "  {prefix}cmm * 100 +"
                "  {prefix}cjj >= {start_date}"
                " AND {prefix}css * 1000000 +"
                "  {prefix}caa * 10000 +"
                "  {prefix}cmm * 100 +"
                "  {prefix}cjj <= {end_date}"
            )

            if self.importer_id.mode == 'final_update':
                where += (
                    " OR {prefix}mss * 1000000 +"
                    "  {prefix}maa * 10000 +"
                    "  {prefix}mmm * 100 +"
                    "  {prefix}mjj >= {start_date}"
                    " AND {prefix}mss * 1000000 +"
                    "  {prefix}maa * 10000 +"
                    "  {prefix}mmm * 100 +"
                    "  {prefix}mjj <= {end_date}"
                    ")"
                )
            else:
                where += ")"
        else:
            where = (
                " {prefix}dss * 1000000 +"
                "  {prefix}daa * 10000 +"
                "  {prefix}dmm * 100 +"
                "  {prefix}djj >= {start_date}"
                " AND {prefix}dss * 1000000 +"
                "  {prefix}daa * 10000 +"
                "  {prefix}dmm * 100 +"
                "  {prefix}djj <= {end_date}"
            )
        return where.format(**query_kwargs)

    def _get_sql_query(self, date_start, date_end, col_names):

        query_kwargs = {
            'schema': self.schema,
            'table_name': self.table_name,
            'prefix': self.table_prefix,
        }

        query = "SELECT * FROM {schema}.{table_name}"

        where = self._get_sql_where_date(date_start, date_end, col_names)
        query += ' WHERE ' + where
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

    def _local_table_exists(self):
        cr = self.env.cr
        odoo_table_name = self._PREFIX + self.table_name.lower()
        cr.execute(
            "SELECT 1 FROM information_schema.tables"
            " WHERE table_name = '{}'".format(odoo_table_name))
        return cr.fetchone()

    @api.multi
    @job(default_channel='root.db2.create_or_update')
    def create_or_update_record(self, db2_id, ref=None):
        """Create or update a record from the DB2 data local copy.

        db2_id: row id to read and convert
        ref: is not used but is there for verification
        """
        return mappers[self.table_name].process(self, self.table_name, db2_id)

    @api.multi
    def create_convertion_jobs(self, where_clause):
        """Create jobs from rows in local copy for a range of dates"""
        eta = max(0, min(self.eta or 2, 23))
        now = datetime.now()
        next_eta = now.replace(hour=eta, minute=0, second=0, microsecond=0)
        # make sure the next eta is in future
        if next_eta < now:
            next_eta += timedelta(days=1)

        cr = self.env.cr
        odoo_table_name = self._PREFIX + self.table_name.lower()

        ref_col = self.table_prefix + 'sui'

        query = (
            "SELECT id, %s FROM %s"
            " WHERE ") % (ref_col, odoo_table_name)
        query += where_clause
        if self.where_clause:
            query += " AND " + self.where_clause
        cr.execute(query)
        rows = cr.fetchall()

        mode = self.importer_id.mode
        priority = self.importer_id.priority

        # Use a sql query to speed up insert of jobs
        # (we have ~440k jobs to create)
        create_job_query = (
            "INSERT INTO queue_job ("
            "func_string,priority,retry,user_id,uuid,record_ids,company_id,"
            "method_name,state,kwargs,channel_method_name,channel,args,"
            "job_function_id,max_retries,date_created,name,model_name,eta)"
            " VALUES ("
            "'db2.importer.table({table_id},)"
            ".create_or_update_record({{record_id}}, {{ref}})',{priority},0,1,"
            "'{{uuid}}','[{table_id}]',1,'create_or_update_record','pending',"
            # escape 2 levels to get {}. {{{{}}}} -> {{}} -> {}
            "'{{{{}}}}','<db2.importer.table>.create_or_update_record',"
            "'root.db2.create_or_update','[{{record_id}}]',2,5,"
            "'{date_created}','db2.importer.table.create_or_update_record',"
            "'db2.importer.table','{eta}')"
        ).format(
            table_id=self.id,
            priority=priority,
            date_created=fields.Datetime.to_string(now),
            eta=fields.Datetime.to_string(next_eta),
        )

        cpt = 0
        for row in rows:
            cpt += 1
            db_id = row[0]
            ref = row[1]
            # Prepare a job to execute the creation
            method_name = 'create_or_update_record'
            model = repr(self)
            func_string = "%s.%s(%s, %s)" % (model, method_name, db_id, ref)
            # skip check of existing job if in history mode
            # for large import of data this creates one extra
            # query useless most of the time.
            if mode != 'history':
                count_job = self.env['queue.job'].search_count(
                    [('model_name', '=', 'db2.importer.table'),
                     ('func_string', '=', func_string),
                     ('state', '!=', 'done')])
                if count_job:
                    continue

            job_id = unicode(uuid.uuid4())
            # self.with_delay(eta=next_eta).create_or_update_record(db_id, ref)
            query = create_job_query.format(
                record_id=db_id,
                uuid=job_id,
                ref=ref)
            cr.execute(query)

            if cpt % 100 == 0 or cpt == len(rows):
                _logger.info(
                    'Job created for %s %s on %s',
                    self.table_name, cpt, len(rows))

    @api.multi
    @job(default_channel='root.db2.generate_jobs')
    def create_convertion_jobs_by_dates(self, date_start, date_end):
        """Create conversion jobs for a range of dates"""
        # No need to pass colname list as we always have
        # a create and modify date on purchase and on sale order
        # unless the model is MVTLOT as css doesn't exist there.
        # but we don't import MVTLOT anymore
        colname = None
        where = self._get_sql_where_date(date_start, date_end, colname)
        self.create_convertion_jobs(where)

    @api.multi
    def requeue_deleted(self):
        """Requeue import for an update of orders with deleted lines

        By forcing the state to 'draft' those orders will be refreshed
        by the update_draft process.

        We don't directly delete them because the ones to be set
        to done needs to go through a list of operation and
        create_or_update_record job will take care of that for us.

        """
        if self.table_name == 'PENTCDFO':
            model = 'purchase.order'
            draft_state = 'purchase'
            table = 'purchase_order'
            db2_table = 'pdetcdfo'
            db2_prefix = 'dcf'
        elif self.table_name == 'PENTCDCL':
            model = 'sale.order'
            draft_state = 'draft'
            table = 'sale_order'
            db2_table = 'pdetcdcl'
            db2_prefix = 'dcc'

        cursor = self.env.cr
        query = (
            "SELECT xol.id"
            " FROM {table}_line AS xol"
            " INNER JOIN {table} AS xo"
            "   ON xo.id = xol.order_id"
            " INNER JOIN db2_{db2_table}"
            "   ON {db2_prefix}sui = xo.name::integer"
            "     AND {db2_prefix}nli = xol.sequence"
            " WHERE deleted = True"
        ).format(table=table, db2_table=db2_table, db2_prefix=db2_prefix)
        cursor.execute(query)
        to_del_ids = [r[0] for r in cursor.fetchall()]
        to_del = self.env[model + '.line'].browse(to_del_ids)

        orders = to_del.mapped('order_id')
        orders.write({'state': draft_state})
        _logger.info(
             '{number} {model} set to {draft_state}'.format(
                 number=len(orders), model=model, draft_state=draft_state))

    @api.multi
    @job(default_channel='root.db2.generate_jobs')
    def create_convertion_jobs_for_draft(self):
        """Create conversion jobs all orders in a draft state
        By draft state we mean the states in which the orders
        are incomplete, thus it is 'purchase' for purchase orders.
        """

        if self.table_name == 'PENTCDFO':
            model = 'purchase.order'
            state = 'purchase'
        elif self.table_name == 'PENTCDCL':
            model = 'sale.order'
            state = 'draft'
        else:
            return

        self.requeue_deleted()

        records = self.env[model].search([('state', '=', state)])
        suite_names = records.mapped('name')

        # filter order name containing non digits
        suite_names = [sn for sn in suite_names if sn and sn.isdigit()]
        suite_names = ','.join(suite_names)

        where = "%ssui IN (%s)" % (self.table_prefix, suite_names)
        self.create_convertion_jobs(where)

    def _get_from_db2(self, date_start, date_end):
        """ fetch table from DB2 on a range of dates """
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
            odoo_table_name = self._PREFIX + self.table_name.lower()

            db2_cr = conn.cursor()
            cr = self.env.cr

            if not self._local_table_exists():
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
            query = self._get_sql_query(date_start, date_end, col_names)
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
        cpt = 0
        for row in rows:
            # Make list of values (x2) for insert and update placeholders
            values = [convert_coding(v) for v in row] * 2
            # Using mogrify to transform DECIMAL in int
            cr.execute(cr.mogrify(query, values))
            cr.fetchone()[0]
            cpt += 1
            if cpt % 10 == 0 or cpt == len(rows):
                _logger.info(
                    'INSERT %s %s on %s', self.table_name, cpt, len(rows))
        self._setup_relations()

    @api.multi
    @job(default_channel='root.db2.fetch')
    def fetch_data(self, date_start, date_end, table_name=None):
        """Fetch data from DB2 and save them as a local copy"""
        csv_date_end = self.csv_until
        # csv doesn't cover the whole fetching
        # considering we won't fetch anything before csv import
        # csv |--------|
        # range1 |---|         fetch nothing
        # range2     |---|     fetch from csv_end to range_end
        # range3         |---| fetch whole range3
        if csv_date_end and csv_date_end > date_end:
            return

        db2_date_start = date_start
        db2_date_end = date_end
        if csv_date_end and csv_date_end > date_start:
            db2_date_start = csv_date_end

        self._get_from_db2(db2_date_start, db2_date_end)
        if self.create_job:
            self.create_convertion_jobs_by_dates(db2_date_start, db2_date_end)


class DB2Importer(models.Model):
    _name = 'db2.importer'

    name = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()

    mode = fields.Selection([
        ('history', 'History'),
        ('final_update', 'Final update')],
        default='history')
    priority = fields.Integer(default=10)
    update_draft = fields.Boolean(
        default=True,
        help="Only for final update"
        )
    fetch = fields.Boolean(
        default=True,
        help="Disable to play only with local copy of data")

    table_ids = fields.One2many('db2.importer.table', 'importer_id')

    @api.multi
    def db2_import(self):

        str_next_start = self.date_start

        for table in self.table_ids:
            if table.create_job:

                # Create jobs for data imported by csv
                if table.csv_until:
                    # here we don't alter start date
                    # to let the possibility to have
                    # different dates on different models
                    # while keeping the jobs creating by dates range
                    # by date range instead of model by model
                    table.with_delay().create_convertion_jobs_by_dates(
                        str_next_start, table.csv_until)

                # Create jobs for history orders to update in final mode
                # always update drafts in final mode
                # replaying draft will help to close older draft orders
                # in advance and also update orders with deleted lines
                if self.update_draft or self.mode == 'final_update':
                    table.with_delay().create_convertion_jobs_for_draft()

        if not self.fetch:
            return

        # split date range per month basis
        dt_next_end = False
        dt_end = fields.Date.from_string(self.date_end)
        while not dt_next_end or dt_next_end < dt_end:
            dt_next_start = fields.Date.from_string(str_next_start)
            month_end = monthrange(dt_next_start.year, dt_next_start.month)[1]
            dt_next_end = min(dt_next_start.replace(day=month_end), dt_end)
            str_next_end = fields.Date.to_string(dt_next_end)
            # get data for each table
            for table in self.table_ids:
                table.with_delay().fetch_data(
                    str_next_start, str_next_end,
                    table.table_name)  # table_name is only added for display
            str_next_start = fields.Date.to_string(
                dt_next_end + timedelta(days=1))
