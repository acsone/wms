# -*- coding: utf-8 -*-

import psycopg2

from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger

from odoo.addons.specific_zetes.tools.domain_interface import Savepoint


# pylint: disable=sql-injection
class TestSavepoint(SavepointCase):
    def _table_exists(self, name):
        query = (
            "SELECT relname FROM pg_class WHERE"
            " relkind IN ('r','v','m') AND relname=%s"
        )
        self.env.cr.execute(query, (name,))
        return self.env.cr.rowcount

    def assert_table_exists(self, name):
        self.assertTrue(self._table_exists(name))

    def assert_table_not_exists(self, name):
        self.assertFalse(self._table_exists(name))

    def create_table(self, name):
        self.env.cr.execute("CREATE TABLE {} ()".format(name))

    def drop_table(self, name):
        self.env.cr.execute("DROP TABLE IF EXISTS {}".format(name))

    def table_name(self, savepoint):
        return "test_savepoint_%s" % (savepoint._name)

    @mute_logger("odoo.sql_db")
    def test_savepoint(self):
        savepoint = Savepoint(self.env.cr)
        name = self.table_name(savepoint)
        self.assert_table_not_exists(name)
        savepoint.start()

        self.create_table(name)
        self.assert_table_exists(name)
        savepoint.rollback()
        self.assert_table_not_exists(name)

        self.create_table(name)
        savepoint.release()
        self.assert_table_exists(name)
        with self.assertRaisesRegexp(psycopg2.InternalError, "no such savepoint"):
            savepoint.release()

    @mute_logger("odoo.sql_db")
    def test_savepoint_context_manager(self):
        with Savepoint(self.env.cr) as savepoint:
            name = self.table_name(savepoint)
            self.assert_table_not_exists(name)
            savepoint.start()

            self.create_table(name)
            self.assert_table_exists(name)
            savepoint.rollback()
            self.assert_table_not_exists(name)

            self.create_table(name)
            savepoint.release()
            self.assert_table_exists(name)

        with self.assertRaisesRegexp(psycopg2.InternalError, "no such savepoint"):
            savepoint.release()
