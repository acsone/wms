# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import pyodbc
import socket

from odoo import api, fields, models


class DB2Importer(models.Model):
    _name = 'db2.importer.table'


    _PREFIX = 'db2_'

    table_name = fields.Char(required=True)
    schema = fields.Char(required=True)
    table_prefix = fields.Char(
        help="3 firsts character on each db2 column")

    last_import = fields.Date()

    importer_id = fields.Many2one('db2.importer')

    def get_from_db2(self, db2_cr, date_start, date_end):
        cr = self.env.cr
        schema='GENDATA'
        table_name = 'pdetcdcl'
        odoo_table_name = self._PREFIX + table_name
        cr.execute(
            "SELECT 1 FROM information_schema.tables"
            " WHERE table_name = '{}'".format(odoo_table_name))
        table_exists = cr.fetchone()

        if not table_exists:
            db2_cr.execute(
                "SELECT column_name, data_type FROM qsys2.syscolumns"
                " WHERE table_schema = '{schema}'"
                " AND table_name = '{table_name}'".format(
                    #schema=self.schema,
                    schema=schema,
                    #table_name=self.table_name))
                    table_name=table_name))
            columns = db2_cr.fetchall()
            if not self.table_prefix:
                self.table_prefix = columns[0][0][:3]
            columns = ["{} {},\n".format(col[0], col[1]) for col in columns]

            cr.execute(
                "CREATE TABLE {} ("
                "id integer PRIMARY KEY,"
                "{}"
                ");").format(odoo_table_name, columns)
            res = cr.fetchone()

        query_kwargs = {
            'start_age': date_start[:2],
            'start_year': date_start[2:4],
            'start_month': date_start[5:7],
            'start_day': date_start[8:],
            'end_age': date_end[:2],
            'end_year': date_end[2:4],
            'end_month': date_end[5:7],
            'end_day': date_end[8:],
            'table_name': table_name,
            'prefix': self.table_prefix,
        }
        query = (
            "SELECT * FROM {t}"
            " WHERE {prefix}css >= '{start_age}'"
            " AND {prefix}css <= {end_age}'"
            " AND {prefix}caa >= {start_year}'"
            " AND {prefix}caa <= {end_year}'"
            " AND {prefix}cmm >= {start_month}'"
            " AND {prefix}cmm <= {end_month}'"
            " AND {prefix}cdd >= {start_day}'"
            " AND {prefix}cdd <= {end_day}'"
            " OR {prefix}mss >= '{start_age}'"
            " AND {prefix}mss <= {end_age}'"
            " AND {prefix}maa >= {start_year}'"
            " AND {prefix}maa <= {end_year}'"
            " AND {prefix}mmm >= {start_month}'"
            " AND {prefix}mmm <= {end_month}'"
            " AND {prefix}mdd >= {start_day}'"
            " AND {prefix}mdd <= {end_day}'"
            ).format(*query_kwargs)
        #query = self._get_sql_query()
        #db2_cr.execute(query, params)



class DB2Importer(models.Model):
    _name = 'db2.importer'

    name = fields.Char()
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
