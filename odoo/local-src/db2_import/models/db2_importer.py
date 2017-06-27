# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import pyodbc
import socket

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class DB2Importer(models.Model):
    _name = 'db2.importer.table'


    _PREFIX = 'db2_'

    schema = fields.Char(required=True)
    table_name = fields.Char(required=True)
    table_prefix = fields.Char(
        help="3 firsts character on each db2 column")

    primary_key = fields.Char()

    last_import = fields.Date()

    importer_id = fields.Many2one('db2.importer')

    def _create_table(self, db2_cr):
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

        query = (
            "CREATE TABLE {} ("
            "id serial PRIMARY KEY,"
            "{}"
            ")".format(odoo_table_name, columns))
        cr.execute(query)
        _logger.info('CREATE TABLE %s', odoo_table_name)

    def get_from_db2(self, db2_cr, date_start, date_end):
        cr = self.env.cr
        odoo_table_name = self._PREFIX + self.table_name.lower()
        get_updates = "get_updates" in self.env.context
        cr.execute(
            "SELECT 1 FROM information_schema.tables"
            " WHERE table_name = '{}'".format(odoo_table_name))
        table_exists = cr.fetchone()

        if not table_exists:
            self._create_table(db2_cr)
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
            #date_end = fields.Date.today()
            date_end = "2017-01-02"

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

        if get_updates:
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
        query = query.format(**query_kwargs)
        db2_cr.execute(query, [])

        rows = db2_cr.fetchall()

        # Save them locally
        columns = rows[0].cursor_description
        column_names = ",".join([col[0] for col in columns])

        insert_query = (
            u"INSERT INTO {table_name} ({column_names})"
             "VALUES ({placeholders})"
        ).format(column_names=column_names,
                 table_name=odoo_table_name,
                 placeholders=','.join(['%s']*len(columns)))
        for row in rows:
            to_update = False
            values = []
            for v in row:
                if isinstance(v, str):
                    v = v.decode('latin_1')
                    v = v.encode('utf8')
                values.append(v)
            if get_updates:
                # check if needed to be updated
                # do a select with primary keys
                to_update = True
            if to_update:
                # TODO
                query = "UPDATE"
            else: # insert
                query = insert_query
            # Using mogrify to transform DECIMAL in int
            cr.execute(cr.mogrify(query, values))
            _logger.info('INSERT 1')

        self.last_import = date_end


class DB2Importer(models.Model):
    _name = 'db2.importer'

    last_import = fields.Date()
    date_start = fields.Date()
    date_end = fields.Date()

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
