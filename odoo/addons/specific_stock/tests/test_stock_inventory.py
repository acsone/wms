# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, datetime as dt

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockInventory(TransactionCase):
    post_install = True
    at_install = False

    def test_date_last_inventory(self):
        """
        Check if the date of the last inventory
        is correctly change when we do an inventory.
        The last inventory date should not change
        when we update the quantity on hand
        :return:
        """
        product = self.env["product.product"].create(
            {"name": "Unittest P1", "uom_id": self.ref("product.product_uom_unit")}
        )
        self.assertFalse(product.date_last_inventory)

        inventory = self.env["stock.inventory"].create(
            {"name": "Test date last inventory", "filter": "product"}
        )
        inventory_line = inventory.line_ids.create(
            {
                "inventory_id": inventory.id,
                "product_id": product.id,
                "product_qty": 20,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        # Validate the inventory
        inventory.action_done()

        # The date_last_inventory date is set to "NOW".
        # It should be the same date than the create date of the line.
        # However, sometime the date_last_inventory date is not really
        # the same than the create date of the line.
        # It's why I check that the date_last_inventory is greater or equal
        # to the create_date of the line.
        self.assertGreaterEqual(product.date_last_inventory, inventory_line.create_date)
        current_date_last_inventory = product.date_last_inventory

        # Now we wil update the quantity on hand with the wizard
        # The date_last_inventory should not change
        wizard_obj = self.env["stock.change.product.qty"]
        update_qty_wizard = wizard_obj.create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": 16,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        update_qty_wizard.change_product_qty()

        self.assertEqual(product.date_last_inventory, current_date_last_inventory)
