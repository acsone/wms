# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockReturnPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockReturnPicking, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, round_autoset=False)
        )
        #  create and execute a picking with 1 product put into a stock quant
        #  package

        # Base data
        StockQuantPackage = cls.env["stock.quant.package"]
        StockReturnPicking = cls.env["stock.return.picking"]

        cls.pack = StockQuantPackage.create({"name": "Pack test"})

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "TOR1",
            }
        )
        wh = cls.env["stock.warehouse"].search([])
        cls.location = wh[0].view_location_id
        cls.location.usage = "internal"
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.pick_type = cls.env.ref("stock.picking_type_out")
        cls.pick_type.subcode = "PICK"

        # Put qty in stock for product
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
                "product_qty": 3,
                "inventory_id": inventory.id,
                "location_id": cls.location.id,
            }
        )
        inventory.action_done()

        # Create picking
        cls.picking = cls.env["stock.picking"].create(
            {
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

        # execute the picking and assign package to operation
        cls.picking.action_assign()
        cls.product_pack_op = cls.picking.pack_operation_ids.filtered(
            lambda o: o.product_id == cls.product
        )
        cls.product_pack_op.write(
            {
                "qty_done": cls.product_pack_op.product_qty,
                "result_package_id": cls.pack.id,
            }
        )
        cls.picking.do_transfer()

        cls.quants = cls.env["stock.quant"].search(
            [
                ("history_ids", "in", cls.move.id),
                ("location_id", "child_of", cls.move.location_dest_id.id),
            ]
        )

        # create a return picking for the executed picking
        cls.stock_return_picking = StockReturnPicking.with_context(
            active_id=cls.picking.id
        ).create({})

    def test_00(self):
        """
        Data:
            A stock return for picking with one product put into a pack
        Test case:
            Execute the stock return
        Expected return:
            The quant is no more linked to a package
        """

        # before the introduction of this test, the unpack operation was done
        # only for pickings with a customer location as destination. We force
        # an other usage to be sure that the unpack is always done
        self.loc_customer.usage = "internal"

        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.quants.package_id)
        self.stock_return_picking.create_returns()["res_id"]
        self.assertFalse(self.quants.package_id)
