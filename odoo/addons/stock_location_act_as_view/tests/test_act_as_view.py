# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import exceptions
from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger


class TestActAsView(SavepointCase):

    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super(TestActAsView, cls).setUpClass()

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "Code product 1",
            }
        )
        cls.location_act_as_view = cls.env["stock.location"].create(
            {"name": "Act as view", "usage": "internal", "act_as_view": True}
        )
        cls.location = cls.env["stock.location"].create(
            {"name": "Internal", "usage": "internal"}
        )

    def _do_inventory(self, product, location):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test unit",
                "filter": "product",
                "location_id": location.id,
                "product_id": product.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.create(
            {
                "product_id": product.id,
                "product_qty": 1.0,
                "inventory_id": inventory.id,
                "location_id": location.id,
            }
        )
        inventory.action_done()

    @mute_logger("odoo.addons.stock_inventory_controller.models.stock_inventory")
    def test_inventory_in_act_as_view_loc(self):
        msg = "You cannot move to a location acting as view"
        with self.assertRaisesRegexp(exceptions.UserError, msg):
            self._do_inventory(self.product_1, self.location_act_as_view)

    def test_inventory_normal_internal_loc(self):
        self._do_inventory(self.product_1, self.location)
