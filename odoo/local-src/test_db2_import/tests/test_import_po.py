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
