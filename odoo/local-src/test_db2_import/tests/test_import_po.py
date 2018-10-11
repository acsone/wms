# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from freezegun import freeze_time

from odoo.addons.db2_import.converter.purchase import DB2MapperPurchaseOrder

from .common import DB2ImportTestCase


class TestImportPO(DB2ImportTestCase):

    _table = 'db2_pentcdfo'
    _suite_col = 'ecfsui'

    def setUp(self):
        super(TestImportPO, self).setUp()
        self.table_name = 'PDETCDFO'
        self.importer_table_po = self.env.ref(
            'db2_import.db2_table_pentcdfo_for_purchase'
        )
        # We want history mode to generate the back orders
        self.importer_table_po.importer_id.mode = 'final_update'

    def check_po_values(self, expected_values):
        self.check_values(self.po, expected_values)

    def check_pol_values(self, expected_values):
        for line in self.po.order_line:
            expected_line_values = None
            for exp in expected_values:
                if exp['sequence'] == line.sequence:
                    expected_line_values = exp
                    break

            self.assertTrue(expected_line_values,
                            msg="Purchase line %s not found" % line.sequence)

            self.check_values(line, expected_line_values)

    @freeze_time("2018-08-11")
    def test_import_po_111523(self):
        """Import PO 111523.

        """
        ref = self.env.ref
        suite = 111523
        db2_id = self.get_row_from_suite(suite)
        DB2MapperPurchaseOrder.process(
            self.importer_table_po, self.table_name, db2_id)
        self.po = self.env['purchase.order'].search(
            [('name', '=', str(suite))])
        self.assertEqual(len(self.po), 1)

        expected_values = [
            {
                'sequence': 10,
                'product_id': ref('__import__.product_5042450'),
            },
            {
                'sequence': 20,
                'product_id': ref('__import__.product_5042265'),
            },
            {
                'sequence': 30,
                'product_id': ref('__import__.product_5043340'),
            },
        ]
        self.check_pol_values(expected_values)

        expected_values = {
            'name': str(suite), 'state': u'purchase',

            'partner_id': ref('__import__.supplier_69000'),
            'date_order': '2018-08-10 00:00:00',
            'date_planned': '2018-08-13 00:00:00',
            'amount_untaxed': 1109.54,
            'amount_tax': 233.0,
            'amount_total': 1342.54,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': False,
            'invoice_status': u'no',

            'responsible_id': False,

            'origin': False,
        }
        self.check_po_values(expected_values)
        self.assertEqual(len(self.po.order_line), 3)
        self.assertEqual(len(self.po.picking_ids), 1)

    @freeze_time("2018-12-31")
    def test_import_history_expired(self):
        """Import PO 111523.

        """
        ref = self.env.ref
        suite = 111523
        db2_id = self.get_row_from_suite(suite)

        self.importer_table_po.importer_id.mode = 'history'

        DB2MapperPurchaseOrder.process(
            self.importer_table_po, self.table_name, db2_id)
        self.po = self.env['purchase.order'].search(
            [('name', '=', str(suite))])
        self.assertEqual(len(self.po), 1)

        expected_values = {
            'name': str(suite), 'state': u'done',

            'partner_id': ref('__import__.supplier_69000'),
        }
        self.check_po_values(expected_values)
        self.assertEqual(len(self.po.order_line), 3)
        self.assertEqual(len(self.po.picking_ids), 0)

    @freeze_time("2018-01-30")
    def test_import_po_106543(self):
        """Import PO 106543.

        Test picking created from PO is in a done state.
        And backorder is confirmed state
        """
        ref = self.env.ref
        suite = 106543
        db2_id = self.get_row_from_suite(suite)

        DB2MapperPurchaseOrder.process(
            self.importer_table_po, self.table_name, db2_id)
        self.po = self.env['purchase.order'].search(
            [('name', '=', str(suite))])
        self.assertEqual(len(self.po), 1)

        expected_values = [
            {
                'sequence': 10,
                'product_id': ref('__import__.product_5052036'),
            },
            {
                'sequence': 20,
                'product_id': ref('__import__.product_5091157'),
            },
            {
                'sequence': 30,
                'product_id': ref('__import__.product_5091155'),
            },
            {
                'sequence': 40,
                'product_id': ref('__import__.product_5029016'),
            },
            {
                'sequence': 50,
                'product_id': ref('__import__.product_7920006'),
            },
            {
                'sequence': 60,
                'product_id': ref('__import__.product_5351536'),
            },
            {
                'sequence': 70,
                'product_id': ref('__import__.product_5350327'),
            },
            {
                'sequence': 80,
                'product_id': ref('__import__.product_7920037'),
            },
            {
                'sequence': 90,
                'product_id': ref('__import__.product_5920461'),
            },
            {
                'sequence': 100,
                'product_id': ref('__import__.product_5920462'),
            },
            {
                'sequence': 110,
                'product_id': ref('__import__.product_5920467'),
            },
            {
                'sequence': 120,
                'product_id': ref('__import__.product_5920468'),
            },
        ]
        self.check_pol_values(expected_values)

        expected_values = {
            'name': str(suite), 'state': u'purchase',

            'partner_id': ref('__import__.supplier_79200'),
            'date_order': '2018-01-19 00:00:00',
            'date_planned': '2018-01-26 00:00:00',
            'amount_untaxed': 499.73,
            'amount_tax': 101.56,
            'amount_total': 601.29,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': False,
            'invoice_status': u'invoiced',

            'responsible_id': False,

            'origin': False,
        }
        self.check_po_values(expected_values)
        self.assertEqual(len(self.po.order_line), 12)
        self.assertEqual(len(self.po.picking_ids), 2)
        self.assertEqual(self.po.picking_ids[0].state, 'done')
        self.assertEqual(self.po.picking_ids[1].state, 'confirmed')

        journal_xid = '__setup__.account_journal_achat_migration'
        journal = ref(journal_xid)
        self.assertEqual(len(self.po.invoice_ids), 1)
        self.assertEqual(
            self.po.invoice_ids.journal_id,
            journal
        )
        self.assertEqual(self.po.invoice_ids.amount_total, 0)

    @freeze_time("2018-08-11")
    def test_import_po_deleted_line(self):
        """Import PO 111523.

        Test reimport with a deleted line.

        """
        ref = self.env.ref
        suite = 111523
        db2_id = self.get_row_from_suite(suite)

        self.importer_table_po.importer_id.mode = 'history'

        DB2MapperPurchaseOrder.process(
            self.importer_table_po, self.table_name, db2_id)
        self.po = self.env['purchase.order'].search(
            [('name', '=', str(suite))])
        self.assertEqual(len(self.po), 1)

        expected_values = [
            {
                'sequence': 10,
                'product_id': ref('__import__.product_5042450'),
            },
            {
                'sequence': 20,
                'product_id': ref('__import__.product_5042265'),
            },
            {
                'sequence': 30,
                'product_id': ref('__import__.product_5043340'),
            },
        ]
        self.check_pol_values(expected_values)

        expected_values = {
            'name': str(suite), 'state': u'purchase',

            'amount_untaxed': 1109.54,
            'amount_tax': 233.0,
            'amount_total': 1342.54,
        }
        self.check_po_values(expected_values)
        self.assertEqual(len(self.po.order_line), 3)
        self.assertEqual(len(self.po.picking_ids), 0)

        cr = self.env.cr
        cr.execute(
            'UPDATE db2_pdetcdfo SET deleted = True'
            '  WHERE dcfsui = 111523 AND dcfnli = 20')

        DB2MapperPurchaseOrder.process(
            self.importer_table_po, self.table_name, db2_id)
        self.po = self.env['purchase.order'].search(
            [('name', '=', str(suite))])

        self.assertEqual(len(self.po), 1)
        self.assertEqual(len(self.po.order_line), 2)

        expected_values = [
            {
                'sequence': 10,
                'product_id': ref('__import__.product_5042450'),
            },
            {
                'sequence': 30,
                'product_id': ref('__import__.product_5043340'),
            },
        ]
        self.check_pol_values(expected_values)
        expected_values = {
            'name': str(suite), 'state': u'purchase',

            'amount_untaxed': 836.31,
            'amount_tax': 175.62,
            'amount_total': 1011.93,
        }
        self.check_po_values(expected_values)
