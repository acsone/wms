# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from odoo.tests.common import SavepointCase


class TestStock(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStock, cls).setUpClass()

        # Create Partner and customer
        cls.partner = cls.env["res.partner"].create({"name": "my b2c partner"})
        cls.customer = cls.partner.copy()

        # Create product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "TOR1",
                "tracking": "none",
            }
        )
        wh = cls.env["stock.warehouse"].search([])
        cls.location = wh[0].view_location_id
        cls.location.usage = "internal"
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")

        cls.pick_type = cls.env.ref("stock.picking_type_out")
        cls.pick_type.subcode = "PICK"

        # Create picking
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "customer_id": cls.customer.id,
                "picking_type_id": cls.pick_type.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking.id,
                "name": "Test move 1a",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 6,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move.action_confirm()

        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test",
                "filter": "product",
                "location_id": cls.location.id,
                "product_id": cls.product.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.unlink()

        inventory.line_ids.create(
            {
                "product_id": cls.product.id,
                "product_qty": 100,
                "inventory_id": inventory.id,
                "location_id": cls.location.id,
            }
        )
        inventory.action_done()

        cls.picking.with_context(round_autoset=False).action_assign()

    def test_1(self):
        # Case 1 : partner wants the labels, customer is b2c : no labels should be printed
        self.picking.partner_id.no_labels_products = False
        self.picking.customer_id.is_b2c_customer = True
        with mock.patch.object(
            self.env["stock.pack.operation"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : no call to the print method
            self.assertEqual(patched_print.call_count, 0)

    def test_2(self):
        # Case 2 : partner wants the labels, customer is not b2c : labels should be printed
        self.picking.partner_id.no_labels_products = False
        self.picking.customer_id.is_b2c_customer = False
        # Check that the products labels are printed for b2c partners
        with mock.patch.object(
            self.env["stock.pack.operation"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : one call to the print method
            self.assertEqual(patched_print.call_count, 1)

    def test_3(self):
        # Case 3 : partner does not want the labels, customer is not b2c : labels should not be printed
        self.picking.partner_id.no_labels_products = True
        self.picking.customer_id.is_b2c_customer = False
        with mock.patch.object(
            self.env["stock.pack.operation"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : no call to the print method
            self.assertEqual(patched_print.call_count, 0)

    def test_4(self):
        # Case 4 : partner does want the labels, customer is b2c : labels should not be printed
        self.picking.partner_id.no_labels_products = True
        self.picking.customer_id.is_b2c_customer = True
        with mock.patch.object(
            self.env["stock.pack.operation"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : no call to the print method
            self.assertEqual(patched_print.call_count, 0)
