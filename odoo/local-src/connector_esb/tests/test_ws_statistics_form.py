# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from .common import ESBXMLTestCase


class WSStatisticsFormTestCase(ESBXMLTestCase):
    def setUp(self):
        super(WSStatisticsFormTestCase, self).setUp()
        self.setup_records()

    def setup_records(self):
        self.partner = self.env['res.partner'].create(
            {'name': 'Foo', 'ref': '123'}
        )
        self.supplier = self.env['res.partner'].create(
            {'name': 'Guerra', 'supplier': True, 'ref': '987654321'}
        )
        categ_med = self.env.ref('specific_data.product_categ_medoc')
        categ_med.esb_ref = 'MED'
        categ_med.is_business_unit = True
        categ_specific_med = self.env['product.category'].create(
            {
                'name': 'specific med',
                'esb_ref': '34',
                'parent_id': categ_med.id,
            }
        )

        categ_ali = self.env.ref('specific_data.product_categ_ali')
        categ_ali.esb_ref = 'ALI'
        categ_ali.is_business_unit = True
        categ_mat = self.env.ref('specific_data.product_categ_materiel')
        categ_mat.esb_ref = 'MAT'
        categ_mat.is_bustiness_unit = True
        product_model = self.env['product.product']
        self.product1 = product_model.create(
            {
                'name': 'KETOFEN 5MG 10CP',
                'default_code': '1021906',
                'categ_id': categ_specific_med.id,
                'seller_ids': [
                    (
                        0,
                        0,
                        {
                            'name': self.supplier.id,
                            'product_code': 'supplier001',
                        },
                    )
                ],
            }
        )
        self.product2 = product_model.create(
            {
                'name': 'EASYPILL CAT 30x10GR',
                'default_code': '2970820',
                'categ_id': categ_ali.id,
                'seller_ids': [
                    (
                        0,
                        0,
                        {
                            'name': self.supplier.id,
                            'product_code': 'supplier001',
                        },
                    )
                ],
            }
        )
        self.product3 = product_model.create(
            {
                'name': 'CAGE PLIANTE DOG RESIDENCE 61x46x53cm',
                'default_code': '8332983',
                'categ_id': categ_mat.id,
            }
        )
        self.product4 = product_model.create(
            {
                'name': 'CALCI BOROGLUCONATE 500ML',
                'default_code': '0135996',
                'categ_id': categ_specific_med.id,
            }
        )
        self.tax_20 = self.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1
        )
        self.tax_20.amount = 20.0

    def create_sale(self, date_order, items):
        """ create a sales order

        ``items`` is a list of tuples:
        (product, quantity, delivered, price_unit, tax)

        """
        sale_model = self.env['sale.order']
        lines = []
        for product, qty, qty_delivered, price_unit, tax in items:
            lines.append(
                {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'product_uom': self.env.ref('product.product_uom_unit').id,
                    'qty_delivered': qty_delivered,
                    'price_unit': price_unit,
                    'tax_id': [(6, 0, tax.ids)],
                    'invoice_status': 'invoiced',
                }
            )
        sale = sale_model.create(
            {
                'partner_id': self.partner.id,
                'date_order': date_order,
                'order_line': [(0, 0, line) for line in lines],
            }
        )
        # force the lines to invoiced, as we filter on invoiced lines, as this
        # is a computed field, we can't set it with ORM
        self.env.cr.execute(
            '''
            UPDATE sale_order_line
            SET invoice_status = 'invoiced'
            WHERE id IN %s
        ''',
            (tuple(sale.order_line.ids),),
        )
        return sale

    def test_message(self):
        self.create_sale(
            '2017-07-26', [(self.product1, 5, 1, 143.2, self.tax_20)]
        )
        self.create_sale(
            '2017-07-26', [(self.product2, 130, 123, 610.9, self.tax_20)]
        )

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('res.partner') as work:
            component = work.component('ws.message.statistics.form')
            options = component.options_for_form(customer_ref='123')
            message = component.get_message(options)

        self.assertXmlEquivalentData(
            message, self.read_test_file('statistics_form_ws_1.xml'), 'sku'
        )

    def test_filter_dates(self):
        self.create_sale(
            '2017-07-20', [(self.product1, 5, 1, 143.2, self.tax_20)]
        )
        self.create_sale(
            '2017-07-26', [(self.product2, 130, 10, 6.0, self.tax_20)]
        )
        self.create_sale(
            '2017-07-30', [(self.product3, 1, 1, 10.0, self.tax_20)]
        )

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('res.partner') as work:
            component = work.component('ws.message.statistics.form')
            options = component.options_for_form(
                customer_ref='123',
                start=date(2017, 7, 22),
                end=date(2017, 7, 28),
            )
            data = component._data_for_message(options)

        # only the sale of 2017-07-26 is considered
        expected = [
            {
                'manufacturer': u'987654321',
                'productName': u'EASYPILL CAT 30x10GR',
                'productType': u'aliment',
                'qtyDelivered': 10.0,
                'sku': u'2970820',
                'taxRate': 20.0,
                'totalPrice': 60.0,
            }
        ]
        self.assertEqual(expected, data)

    def test_filter_product_type(self):
        self.create_sale(
            '2017-07-20', [(self.product1, 5, 1, 143.2, self.tax_20)]
        )
        self.create_sale(
            '2017-07-26', [(self.product2, 130, 10, 6.0, self.tax_20)]
        )
        self.create_sale(
            '2017-07-30', [(self.product3, 1, 1, 10.0, self.tax_20)]
        )

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('res.partner') as work:
            component = work.component('ws.message.statistics.form')
            options = component.options_for_form(
                customer_ref='123', product_type='ALI'
            )
            data = component._data_for_message(options)

        # only the sale of product2 (type aliment) is considered
        expected = [
            {
                'manufacturer': u'987654321',
                'productName': u'EASYPILL CAT 30x10GR',
                'productType': u'aliment',
                'qtyDelivered': 10.0,
                'sku': u'2970820',
                'taxRate': 20.0,
                'totalPrice': 60.0,
            }
        ]
        self.assertEqual(expected, data)

    def test_filter_supplier(self):
        supplier_foo = self.env['res.partner'].create(
            {'name': 'Foo', 'supplier': True, 'ref': '10'}
        )
        supplier_bar = self.env['res.partner'].create(
            {'name': 'Bar', 'supplier': True, 'ref': '11'}
        )
        self.product4.seller_ids = [(5, 0), (0, 0, {'name': supplier_foo.id})]
        self.product3.seller_ids = [(5, 0), (0, 0, {'name': supplier_bar.id})]
        self.create_sale(
            '2017-07-20', [(self.product4, 5, 1, 143.2, self.tax_20)]
        )
        self.create_sale(
            '2017-07-26', [(self.product2, 130, 10, 6.0, self.tax_20)]
        )
        self.create_sale(
            '2017-07-30', [(self.product3, 1, 1, 10.0, self.tax_20)]
        )

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('res.partner') as work:
            component = work.component('ws.message.statistics.form')
            options = component.options_for_form(
                customer_ref='123', suppliers=['987654321', '10']
            )
            data = component._data_for_message(options)

        # we should have product1 and product2 which are sold by the
        # suppliers we asked
        expected = [
            {
                'manufacturer': u'10',
                'productName': u'CALCI BOROGLUCONATE 500ML',
                'productType': u'medicament',
                'qtyDelivered': 1.0,
                'sku': u'0135996',
                'taxRate': 20.0,
                'totalPrice': 143.2,
            },
            {
                'manufacturer': u'987654321',
                'productName': u'EASYPILL CAT 30x10GR',
                'productType': u'aliment',
                'qtyDelivered': 10.0,
                'sku': u'2970820',
                'taxRate': 20.0,
                'totalPrice': 60.0,
            },
        ]
        self.assertEqual(sorted(expected), sorted(data))

    def test_language(self):
        # add some translation
        product = self.product1
        product.with_context(lang='tlh_TLH').name = product.name + ' (TLH)'

        self.create_sale(
            '2017-07-20', [(self.product1, 5, 1, 143.2, self.tax_20)]
        )

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('res.partner') as work:
            component = work.component('ws.message.statistics.form')
            options = component.options_for_form(
                customer_ref='123', language='TLH'
            )
            data = component._data_for_message(options)

        # only the sale of 2017-07-26 is considered
        expected = [
            {
                'manufacturer': u'987654321',
                'productName': u'KETOFEN 5MG 10CP (TLH)',
                'productType': u'medicament',
                'qtyDelivered': 1.0,
                'sku': u'1021906',
                'taxRate': 20.0,
                'totalPrice': 143.2,
            }
        ]
        self.assertEqual(expected, data)
