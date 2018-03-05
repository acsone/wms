# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.db2_import.models.db2_importer import DB2MapperSaleOrder

from .common import DB2ImportTestCase


class TestImportSO(DB2ImportTestCase):

    _table = 'db2_pentcdcl'
    _suite_col = 'eccsui'

    def setUp(self):
        super(TestImportSO, self).setUp()
        self.table_name = 'PDETCDCL'
        self.importer_table_so = self.env.ref(
            'db2_import.db2_table_pentcdcl_for_sale'
        )
        # We want history mode to generate the back orders
        self.importer_table_so.importer_id.mode = 'final_update'

    def check_so_values(self, expected_values):
        for k, expect in expected_values.iteritems():
            if expect is False:
                self.assertFalse(self.so[k],
                                 msg="Field %s must be false" % k)
            elif isinstance(expect, float):
                self.assertAlmostEqual(self.so[k], expect,
                                       msg="Wrong value on field %s" % k)
            else:
                self.assertEqual(self.so[k], expect,
                                 msg="Wrong value on field %s" % k)

    def test_import_history_to_final_update_done(self):
        suite = 2798516
        db2_id = self.get_row_from_suite(suite)

        self.importer_table_so.importer_id.mode = 'history'
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'done',
            'invoice_status': u'invoiced',
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 1)
        self.assertEqual(len(self.so.picking_ids), 0)

        self.importer_table_so.importer_id.mode = 'final_update'

        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'done',
            'invoice_status': u'invoiced',
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 1)
        self.assertEqual(len(self.so.picking_ids), 0)

        self.importer_table_so.importer_id.mode = 'final_update'

    def test_import_history_to_final_update_partial(self):
        suite = 2844358
        db2_id = self.get_row_from_suite(suite)

        self.importer_table_so.importer_id.mode = 'history'
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'draft',
            'invoice_status': u'no',
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 4)
        self.assertEqual(len(self.so.picking_ids), 0)

        self.importer_table_so.importer_id.mode = 'final_update'

        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'sale',
            'invoice_status': u'to invoice',
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 4)
        # self.assertEqual(len(self.so.picking_ids), 3)  # FIXME 4 on int

    def test_import_so_2798516(self):
        """Import SO 2798516.

        1 line with 1 qty SO fully delivered
        no promotion
        """
        ref = self.env.ref
        suite = 2798516
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'done',

            'partner_id': ref('__import__.customer_4362'),
            'partner_invoice_id': ref('__import__.customer_4362'),
            'partner_shipping_id': ref('__import__.customer_4362'),
            'client_order_ref': '20286',
            'suite_name': False,

            'date_order': '2017-11-07 00:00:00',
            'confirmation_date': '2017-11-07 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb2'),
            'supplier_promotion_allowed': False,
            'discount_pricelist_id': ref('__setup__.pricelist_12'),

            'amount_untaxed': 7.16,
            'amount_tax': 1.5,
            'amount_total': 8.66,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'invoiced',

            'user_id': False,

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 1)
        self.assertEqual(len(self.so.picking_ids), 0)

    def test_import_so_2814640(self):
        """Import SO 2814640,
         1 line with 4 qty SO fully delivered
        with promotion
        """
        ref = self.env.ref
        suite = 2814640
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'done',

            'partner_id': ref('__import__.customer_9134'),
            'partner_invoice_id': ref('__import__.customer_9134'),
            'partner_shipping_id': ref('__import__.customer_9134'),
            'client_order_ref': '1710563500000',
            'suite_name': False,

            'date_order': '2017-12-03 00:00:00',
            'confirmation_date': '2017-12-03 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_100'),

            'amount_untaxed': 6.92,
            'amount_tax': 1.45,
            'amount_total': 8.37,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'invoiced',

            'user_id': ref('__setup__.res_user_20'),  # Fabrice

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 1)
        self.assertEqual(len(self.so.picking_ids), 0)

    def test_import_so_2835999(self):
        """Import SO 2835999.

        1 line with 1 qty SO fully delivered
        with antibio tax

        """
        ref = self.env.ref
        suite = 2835999
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'done',

            'partner_id': ref('__import__.customer_4590'),
            'partner_invoice_id': ref('__import__.customer_4590'),
            'partner_shipping_id': ref('__import__.customer_4590'),
            'client_order_ref': '1810408201100',
            'suite_name': False,

            'date_order': '2018-01-10 00:00:00',
            'confirmation_date': '2018-01-10 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_312'),

            'amount_untaxed': 8.31,
            'amount_tax': 0.51,
            'amount_total': 8.82,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'invoiced',

            'user_id': ref('__setup__.res_user_12'),  # Muriel

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 1)
        self.assertEqual(len(self.so.picking_ids), 0)

    def test_import_so_2797926(self):
        """Import SO 2797926.

        Fully delivered order many lines (13)
        """
        ref = self.env.ref
        suite = 2797926
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'done',

            'partner_id': ref('__import__.customer_8857'),
            'partner_invoice_id': ref('__import__.customer_8857'),
            'partner_shipping_id': ref('__import__.customer_8857'),
            'client_order_ref': '1710258702763',
            'suite_name': False,

            'date_order': '2017-11-06 00:00:00',
            'confirmation_date': '2017-11-06 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_312'),

            'amount_untaxed': 449.20,
            'amount_tax': 54.53,
            'amount_total': 503.73,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'invoiced',

            'user_id': ref('__setup__.res_user_19'),  # Patricia

            'origin': '175785058502763',
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 13)
        self.assertEqual(len(self.so.picking_ids), 0)

    def test_import_so_2842879(self):
        """Import SO 2842879.

        Test no duplicates

        """
        ref = self.env.ref
        suite = 2842879
        db2_id = self.get_row_from_suite(suite)
        # Call process twice this must update it not create a duplicate
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'done',

            'partner_id': ref('__import__.customer_4778'),
            'partner_invoice_id': ref('__import__.customer_4778'),
            'partner_shipping_id': ref('__import__.customer_4778'),
            'client_order_ref': '1810275900000',
            'suite_name': False,

            'date_order': '2018-01-22 00:00:00',
            'confirmation_date': '2018-01-22 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_311'),

            'amount_untaxed': 7.69,
            'amount_tax': 1.61,
            'amount_total': 9.30,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'invoiced',

            'user_id': ref('__setup__.res_user_19'),  # Patricia

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 1)
        self.assertEqual(len(self.so.picking_ids), 0)

    def test_import_so_2833868(self):
        """Import SO 2833868.

        partial delivery with Ali, Med, Mat and Fridge products
        one line not delivered

        """
        ref = self.env.ref
        suite = 2833868
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'sale',

            'partner_id': ref('__import__.customer_148'),
            'partner_invoice_id': ref('__import__.customer_148'),
            'partner_shipping_id': ref('__import__.customer_148'),
            'client_order_ref': '1810142300013',
            'suite_name': False,

            'date_order': '2018-01-07 00:00:00',
            'confirmation_date': '2018-01-07 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_105'),

            'amount_untaxed': 72.03,
            'amount_tax': 13.25,
            'amount_total': 85.28,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'to invoice',

            'user_id': ref('__setup__.res_user_12'),  # Muriel

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 7)
        # self.assertEqual(len(self.so.picking_ids), 2)  # FIXME 4 on int

    def test_import_so_2835952(self):
        """Import SO 2835952.

        partial delivery with Med and Mat products
        one line not delivered

        """
        ref = self.env.ref
        suite = 2835952
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'sale',

            'partner_id': ref('__import__.customer_752'),
            'partner_invoice_id': ref('__import__.customer_752'),
            'partner_shipping_id': ref('__import__.customer_752'),
            'client_order_ref': '1810318900007',
            'suite_name': False,

            'date_order': '2018-01-10 00:00:00',
            'confirmation_date': '2018-01-10 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_312'),

            'amount_untaxed': 24.33,
            'amount_tax': 2.29,
            'amount_total': 26.62,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'to invoice',

            'user_id': ref('__setup__.res_user_19'),  # Patricia

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 2)
        # self.assertEqual(len(self.so.picking_ids), 3)  # FIXME

    def test_import_so_2835987(self):
        """Import SO 2835987.

        partial delivery with Med products
        one line not delivered
        TODO: probably accessories

        """
        ref = self.env.ref
        suite = 2835987
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'sale',

            'partner_id': ref('__import__.customer_5651'),
            'partner_invoice_id': ref('__import__.customer_5651'),
            'partner_shipping_id': ref('__import__.customer_5651'),
            'client_order_ref': '1810262400000',
            'suite_name': False,

            'date_order': '2018-01-10 00:00:00',
            'confirmation_date': '2018-01-10 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_108'),

            'amount_untaxed': 8.65,
            'amount_tax': 1.82,
            'amount_total': 10.47,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'to invoice',

            'user_id': ref('__setup__.res_user_2'),  # Raymond

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 2)
        # self.assertEqual(len(self.so.picking_ids), 2)  # FIXME 3 on int

    def test_import_so_2842972(self):
        """Import SO 2842972.

        partial delivery with lot of lines (10)

        Tax 0% EU L

        """
        ref = self.env.ref
        suite = 2842972
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'sale',

            'partner_id': ref('__import__.customer_9003'),
            'partner_invoice_id': ref('__import__.customer_9003'),
            'partner_shipping_id': ref('__import__.customer_9003'),
            'client_order_ref': False,
            'suite_name': False,

            'date_order': '2018-01-22 00:00:00',
            'confirmation_date': '2018-01-22 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_210'),

            'amount_untaxed': 865.64,
            'amount_tax': 0,
            'amount_total': 865.64,
            'currency_id': ref('base.EUR'),

            # Régime Intra-Communautaire
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_3'),
            'invoice_status': u'to invoice',

            'user_id': False,

            'origin': False,
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 10)
        # self.assertEqual(len(self.so.picking_ids), 3)  # FIXME 5 on int

    def test_import_so_2844358(self):
        """Import SO 2844358.

        partial delivery with one line partially delivered

        """
        ref = self.env.ref
        suite = 2844358
        db2_id = self.get_row_from_suite(suite)
        DB2MapperSaleOrder.process(
            self.importer_table_so, self.table_name, db2_id)
        self.so = self.env['sale.order'].search([('name', '=', str(suite))])
        self.assertEqual(len(self.so), 1)
        expected_values = {
            'name': str(suite), 'state': u'sale',

            'partner_id': ref('__import__.customer_4590'),
            'partner_invoice_id': ref('__import__.customer_4590'),
            'partner_shipping_id': ref('__import__.customer_4590'),
            'client_order_ref': '1810408201111',
            'suite_name': False,

            'date_order': '2018-01-23 00:00:00',
            'confirmation_date': '2018-01-23 00:00:00',
            'pricelist_id': ref('specific_data.product_pricelist_pb1'),
            'supplier_promotion_allowed': True,
            'discount_pricelist_id': ref('__setup__.pricelist_312'),

            'amount_untaxed': 45.46,
            'amount_tax': 9.55,
            'amount_total': 55.01,
            'currency_id': ref('base.EUR'),

            # Régime National
            'fiscal_position_id': ref('l10n_be.1_fiscal_position_template_1'),
            'invoice_status': u'to invoice',

            'user_id': ref('__setup__.res_user_12'),  # Muriel

            'origin': '18100001111',
        }
        self.check_so_values(expected_values)
        self.assertEqual(len(self.so.order_line), 4)
        # self.assertEqual(len(self.so.picking_ids), 3)  # FIXME 4 on int
