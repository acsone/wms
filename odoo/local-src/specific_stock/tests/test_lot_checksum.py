# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.exceptions import Warning
from odoo.tests.common import TransactionCase, at_install, post_install


class TestLotChecksum(TransactionCase):
    def setUp(self):
        super(TestLotChecksum, self).setUp()

        stock_location_obj = self.env['stock.location']
        self.location_pa11 = stock_location_obj.create(
            {
                'name': 'Product PA11',
                'kind': 'parking',
                'zone': 'A',
                'corridor': 'P',
                'shelf': 'A',
                'height': '1',
                'box': '1',
            }
        )

        self.location_pb11 = stock_location_obj.create(
            {
                'name': 'Product PB11',
                'kind': 'parking',
                'zone': 'A',
                'corridor': 'P',
                'shelf': 'B',
                'height': '1',
                'box': '1',
            }
        )

        self.location_pe11 = stock_location_obj.create(
            {
                'name': 'Product PE35',
                'kind': 'parking',
                'zone': 'A',
                'corridor': 'P',
                'shelf': 'E',
                'height': '3',
                'box': '5',
            }
        )

        self.product = self.env['product.product'].create({'name': 'Test'})
        self.product.stock_bin_ids.create(
            {
                'location_id': self.location_pa11.id,
                'bin_location_id': self.location_pa11.id,
                'product_id': self.product.product_tmpl_id.id,
            }
        )
        self.product.stock_bin_ids.create(
            {
                'location_id': self.location_pb11.id,
                'bin_location_id': self.location_pb11.id,
                'product_id': self.product.product_tmpl_id.id,
            }
        )

        self.product_2 = self.env['product.product'].create({'name': 'Test 2'})
        self.product_2.stock_bin_ids.create(
            {
                'location_id': self.location_pe11.id,
                'bin_location_id': self.location_pe11.id,
                'product_id': self.product_2.product_tmpl_id.id,
            }
        )

    @post_install(True)
    @at_install(False)
    def test_compute_checksum(self):
        """
        This test will change the checksum size to have maximum 9 checksum.
        After that we will generate 9 lots.
        Each lot should have a different checksum.
        After that we will create a new lot
        and checksum if the method raise an error.
        :return:
        """
        # Change the checksum size
        self.env['ir.config_parameter'].set_param('lot_checksum_size', 1)

        # Archive all checksum
        self.env['stock.production.lot'].search([]).write(
            {'is_archived': True}
        )

        used_checksum = []
        for index in range(9):
            lot = self.env['stock.production.lot'].create(
                {
                    'name': 'test_{}'.format(index),
                    'product_id': self.product.id,
                    'life_date': fields.Datetime.now(),
                }
            )
            self.assertIsNotNone(
                lot.checksum, 'The checksum should not be empty'
            )
            self.assertNotIn(
                lot.checksum,
                used_checksum,
                'The checksum {} has already '
                'been assigned'.format(lot.checksum),
            )

            used_checksum.append(lot.checksum)

        lot_values = {
            'name': 'test_10',
            'product_id': self.product.id,
            'life_date': fields.Datetime.now(),
        }

        # All checksum are assigned for this range (APA=>APD)
        with self.assertRaises(Warning):
            self.env['stock.production.lot'].create(lot_values)

        # We will generate a new checksum with a product in the shelf APE
        # This method shouldn't raise an error.
        lot = self.env['stock.production.lot'].create(
            {
                'name': 'test_product_2',
                'product_id': self.product_2.id,
                'life_date': fields.Datetime.now(),
            }
        )
        self.assertIsNotNone(lot.checksum, 'The checksum should not be empty')
