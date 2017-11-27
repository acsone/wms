# -*- coding: utf-8 -*-

from .. import constants
from .zetes_test_classes import ZetesParkingTest


class TestFullParking(ZetesParkingTest):

    def setUp(self):
        super(TestFullParking, self).setUp()

        # Product 2
        # Location: GAD515
        self.product_2 = self.env['product.product'].create({
            'name': 'Test medoc 2',
            'default_code': '587502',
            'categ_id': self.env.ref('specific_data.product_categ_medoc').id,
            'tracking': 'lot',
            'list_price': 5,
        })

        self.location_product_2 = self.env['stock.location'].create({
            'name': 'GD03B2',
            'kind': 'bin',
            'zone': 'G',
            'corridor': 'D',
            'shelf': '03',
            'height': 'B',
            'box': '2',
            'location_id': self.parent_location.id,
            'bin_checksum_1': '456',
            'bin_checksum_2': '456',
        })
        self.env['stock.location']._parent_store_compute()

        # Set a quantity in this parking
        update_qty_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_2.id,
            'product_tmpl_id': self.product_2.product_tmpl_id.id,
            'new_quantity': 20,
            'location_id': self.parking_medoc.id
        })
        update_qty_wizard.change_product_qty()

        self.reserve_medicament = self.env['stock.location'].create({
            'name': 'GD5'
        })
