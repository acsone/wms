# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import tools
from odoo.addons.connector_esb.models.product.exporter import (
    ProductExportMapper,
)

from .common import ESBXMLTestCase


class ExportProductTestCase(ESBXMLTestCase):
    def setUp(self):
        super(ExportProductTestCase, self).setUp()
        ProductExportMapper.translatable_keys = {'tlh_TLH': {'name': 'Refdem'}}
        self.setup_records()
        self.timestamp = self.env.ref('connector_esb.esb_timestamp_product')
        self.maxDiff = None

    @property
    def model(self):
        return self.env['product.product']

    def setup_records(self):
        supplier = self.env['res.partner'].create(
            {'name': 'Supplier', 'supplier': True, 'ref': '79001'}
        )
        supplier2 = self.env['res.partner'].create(
            {'name': 'Supplier2', 'supplier': True, 'ref': '65852'}
        )
        manufacturer = self.env['res.partner'].create(
            {'name': 'Manufacturer', 'supplier': True, 'ref': 'manu01'}
        )
        self.p_cat_all = self.env.ref('product.product_category_all')
        self.p_cat = self.env.ref('specific_data.product_categ_humain')
        # Set the esb_ref of the business unit
        self.p_cat.parent_id.esb_ref = 'medicament'
        self.p_cat.with_context({'lang': 'nl_BE'}).warning_info = 'Aandacht'
        self.p_cat.with_context({'lang': 'fr_BE'}).warning_info = 'Attention'
        self.p_cat.with_context({'lang': 'de_DE'}).warning_info = 'Aufmerksam'

        tax = self.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1
        )
        tax.esb_ref = '006'
        tax.contrib_sku = 'BBB'
        tax2 = tax.copy(default={'esb_ref': '009', 'contrib_sku': 'CCC'})

        unit = self.env.ref('product.product_uom_unit')
        unit.rounding = 1.0
        unit.esb_ref = "0"
        cm = self.env.ref('product.product_uom_cm')
        cm.rounding = 0.001
        cm.esb_ref = "2"

        ali = self.env.ref('specific_product.product_price_category_ali')
        alg = self.env.ref('specific_product.product_price_category_alg')
        alh = self.env.ref('specific_product.product_price_category_alh')

        self.additional_product = self.env.ref('product.product_product_4')
        self.additional_product.default_code = 'SKU_FREE'

        self.all_records = self.model.browse()
        self.all_records |= self.model.create(
            {
                'name': 'Export me pls',
                'web_published': True,
                'categ_id': self.p_cat.id,
                'default_code': 'exportable001',
                'type': 'product',
                'barcode': 'XXX0001',
                'cnk_code': 'CNK_001',
                'weight': 10.0,
                'depth': 7.0,
                'length': 8.5,
                'width': 9.0,
                'volume': 0.01,
                'tracking': 'lot',
                'uom_id': unit.id,
                'uom_po_id': unit.id,
                'price_category_id': ali.id,
                'taxes_id': [(4, tax.id)],
                'manufacturer': manufacturer.id,
                'seller_ids': [
                    (
                        0,
                        0,
                        {'name': supplier.id, 'product_code': 'supplier001'},
                    )
                ],
                'route_ids': [
                    (4, self.env.ref('stock.route_warehouse0_mto').id)
                ],
                'storage_temperature_id': self.env.ref(
                    'specific_product.product_storage_temperature_6'
                ).id,
            }
        )
        self.all_records |= self.model.create(
            {
                'name': 'Export me pls 2',
                'web_published': False,
                'categ_id': self.p_cat_all.id,
                'default_code': 'exportable002',
                'type': 'product',
                'barcode': 'XXX0002',
                'cnk_code': 'CNK_002',
                'weight': 5.0,
                'depth': 17.0,
                'length': 18.5,
                'width': 19.0,
                'volume': 0.005,
                'tracking': 'serial',
                'unit_in_shrink_wrap': 4,
                'uom_id': cm.id,
                'uom_po_id': cm.id,
                'price_category_id': alg.id,
                'taxes_id': [(4, tax2.id)],
                'seller_ids': [
                    (
                        0,
                        0,
                        {'name': supplier2.id, 'product_code': 'supplier002'},
                    )
                ],
                'route_ids': [
                    (4, self.env.ref('purchase.route_warehouse0_buy').id)
                ],
                'storage_temperature_id': self.env.ref(
                    'specific_product.product_storage_temperature_minus_12'
                ).id,
            }
        )
        self.all_records |= self.model.create(
            {
                'name': 'Export me pls 3',
                'web_published': True,
                'default_code': 'exportable003',
                'type': 'consu',
                'barcode': 'XXX0003',
                'cnk_code': 'CNK_003',
                'weight': 2.5,
                'volume': 1.0,
                'depth': 27.0,
                'length': 28.5,
                'width': 29.0,
                'active': False,
                'tracking': 'none',
                'uom_id': unit.id,
                'uom_po_id': unit.id,
                'ratio_main_product': 5,
                'ratio_additional_product': 1,
                'additional_product_id': self.additional_product.id,
                'price_category_id': alh.id,
                'taxes_id': [(4, tax.id)],
                'seller_ids': [
                    (
                        0,
                        0,
                        {'name': supplier.id, 'product_code': 'supplier003'},
                    )
                ],
                'route_ids': [
                    (4, self.env.ref('stock.route_warehouse0_mto').id),
                    (4, self.env.ref('purchase.route_warehouse0_buy').id),
                ],
            }
        )

        self.force_create_date(self.all_records, '2017-07-13 00:00:00')

        # add some translation
        for rec in self.all_records:
            rec.with_context(lang='tlh_TLH').name = rec.name + ' (TLH)'

        self.unexportable_records = self.model.browse()
        nx1 = self.model.create(
            {
                'name': 'DO NOT Export me',
                # default_code starts with `8888`
                'default_code': '8888_not_exportable001',
            }
        )
        self.all_records |= nx1
        self.unexportable_records |= nx1
        nx2 = self.model.create(
            {'name': 'DO NOT Export me 2', 'default_code': 'not_exportable002'}
        )
        # too old
        self.force_create_date(nx2, '2014-07-28 00:00:00')
        self.all_records |= nx2
        self.unexportable_records |= nx2

        # TODO: add 3rd condition based on "GESCHR!=’L’ (non livrables)"
        # self.all_records |= self.model.create({
        #     'name': 'DO NOT Export me 3',
        #     'default_code': '8888_not_exportable003',
        # })

    def force_create_date(self, records, dt):
        self.env.cr.execute(
            'UPDATE {} SET create_date=%s '
            'WHERE id in %s'.format(self.model._table),
            (dt, tuple(records.ids)),
        )

    def test_mapper(self):
        expected = {
            'Gesdem': 'Export me pls',
            'Gesart': 'exportable001',
            'Cplz05': 'XXX0001',
            'Gespnt': '10.000',
            'Refdem': 'Export me pls (TLH)',
            'Gesarc': 'supplier001',
            'Gescgr': '6',
            'Gescsg': '15',
            'Gesfou': '79001',
            'Cplz25': 'manu01',
            'Gesunv': '0',
            'Gescrt': '2017/07/13',
            'Cplz19': 1,
            'Gescde': 1,
            'Cp2z08': '10.00',
            'Gescsa': 1,
            'Gesctv': '006',
            'Cplz03': 'CNK_001',
            'Gescge': 0,
            'Cplz07': 'BBB',
            'Cp2z01': '7.00',
            'Cp2z03': '8.50',
            'Cp2z05': '9.00',
            'GMA': False,
            'ALI': True,
            'ALG': False,
            'ALH': False,
            'IMP': False,
            # fixed values
            'Cp2z22': '',
            'Warceg': 'Aufmerksam',
            'Warcfr': 'Attention',
            'Warcnl': 'Aandacht',
            'Cp2z02': 0,
            'Cp2z23': 0,
            'Cp2z24': 0,
            'Cp2z17': '6',
            'Cp2z19': 0,
            'Cplz14': 'medicament',
            'Gescov': 0,
            'poids_net-unit': 'KILOGRAM',
            'volume-unit': 'CUBIC_CENTIMETER',
            'hauteur-unit': 'CENTIMETER',
            'longueur-unit': 'CENTIMETER',
            'largeur-unit': 'CENTIMETER',
        }
        rec = self.all_records[0]
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_filename(self):
        self.check_filename('Products_{}.xml')

    @tools.mute_logger('dicttoxml')
    def test_record_exporter_local(self):
        self.timestamp.writer = 'local'
        records = self.all_records - self.unexportable_records
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage='record.exporter')
            respath = exporter.run(records)
            self.addCleanup(os.remove, respath)
        with open(respath, 'r') as result_file:
            result = result_file.read()
        self.assertXmlEquivalentData(
            result, self.read_test_file('product_export_1.xml'), 'Gesart'
        )
        # self.assertXmlEquivalentOutputs(
        #     self.flatten(result),
        #     self.flatten(self.read_test_file('product_export_1.xml'))
        # )

    def test_record_cron_exporter(self):
        """ All record are exported. Unactive ones as well."""
        self.timestamp.writer = 'local'
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage='record.exporter.cron')

        items = exporter.get_items('')
        self.assertEqual(
            len(items),
            self.env['product.product']
            .with_context(active_test=False)
            .search_count([('default_code', 'not like', '8888%')]),
        )

    def test_mapper_specific_fields(self):
        """ Checking some specific parts on the mapper.

        Check the warning messages are not more than 255 chars long.
        """
        self.p_cat.with_context({'lang': 'nl_BE'}).warning_info = (
            'Aandacht__' * 26
        )
        self.p_cat.with_context({'lang': 'fr_BE'}).warning_info = (
            'Attention_' * 26
        )
        self.p_cat.with_context({'lang': 'de_DE'}).warning_info = (
            'Aufmerksam' * 26
        )
        rec = self.all_records[0]
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            mapper = work.component(usage='export.mapper')
            values = mapper.map_record(rec).values()
            self.assertEqual(len(values['Warceg']), 254)
            self.assertEqual(len(values['Warcfr']), 254)
            self.assertEqual(len(values['Warcnl']), 254)
