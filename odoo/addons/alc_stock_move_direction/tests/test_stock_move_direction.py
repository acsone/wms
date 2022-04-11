# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockMoveDirection(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMoveDirection, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True,))
        if "round.instance" in cls.env:
            cls.env = cls.env(context=dict(cls.env.context, round_autoset=False))

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "Code product",
            }
        )

        wh = cls.env["stock.warehouse"].search([], limit=1)
        cls.wh = wh
        cls.wh2 = wh.copy({"name": "wh2", "code": "wh2_code"})
        cls.location = wh.view_location_id
        cls.stock_location = wh.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")

        cls.pick_type_in = cls.env.ref("stock.picking_type_out")
        cls.pick_type_out = cls.env.ref("stock.picking_type_in")

        cls.ResPartner = cls.env["res.partner"]
        cls.supplier = cls.ResPartner.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )
        cls.customer = cls.ResPartner.create(
            {"name": "Unittest customer", "ref": "abc"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.StockLocation = cls.env["stock.location"]
        cls.reception_location = cls.StockLocation.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "internal",
                "act_as_view": True,
            }
        )
        cls.bin1 = cls.StockLocation.create(
            {
                "name": "bin1",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        wiz = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "new_quantity": 10,
                "location_id": cls.bin1.id,
            }
        )
        wiz.change_product_qty()
        cls.StockLocation._parent_store_compute()
        cls.StockPicking = cls.env["stock.picking"]
        picking = cls.StockPicking.create(
            {
                "picking_type_id": cls.pick_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move 1",
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.reception_location.id,
                        },
                    )
                    for product in cls.product
                ],
            }
        )
        cls.incoming_picking = picking.with_context(test_mode=1)

        picking = cls.StockPicking.create(
            {
                "picking_type_id": cls.pick_type_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move 1",
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                    for product in cls.product
                ],
            }
        )
        cls.outgoing_picking = picking.with_context(test_mode=1)

    def test_incoming_move(self):
        # here we have a move from seller to reception under stock
        self.assertTrue(self.incoming_picking.move_lines._is_incoming())
        # once the picking is  condirmerd, the check is done on the pack_operation
        self.incoming_picking.action_assign()
        self.assertTrue(self.incoming_picking.move_lines._is_incoming())
        # if I set a location dest into the pack not under stock
        # this one us used into the compute
        self.incoming_picking.pack_operation_ids.location_dest_id = (
            self.customer_location
        )
        self.assertFalse(self.incoming_picking.move_lines._is_incoming())
        # if we have no pack operation, the destination on move is used to know
        # if the picking is incoming
        self.incoming_picking.pack_operation_ids.unlink()
        self.assertTrue(self.incoming_picking.move_lines._is_incoming())

    def test_outgoing_move(self):
        # here we have a move from stock to customer
        self.assertTrue(self.outgoing_picking.move_lines._is_outgoing())
        # once the picking is  condirmerd, the check is done on the pack_operation
        self.outgoing_picking.action_assign()
        self.assertTrue(self.outgoing_picking.move_lines._is_outgoing())
        # if I set a location dest into the pack not under stock
        # this one us used into the compute
        self.outgoing_picking.pack_operation_ids.location_dest_id = (
            self.stock_location.id
        )
        self.assertFalse(self.outgoing_picking.move_lines._is_outgoing())
        # if we have no pack operation, the destination on move is used to know
        # if the picking is outgoing
        self.outgoing_picking.pack_operation_ids.unlink()
        self.assertTrue(self.outgoing_picking.move_lines._is_outgoing())

    def test_wh_transfer_move(self):
        # in this case: origin and dest are 2 locations under a stock location
        # but into different warehouses
        self.assertTrue(self.outgoing_picking.move_lines._is_outgoing())
        self.assertFalse(self.outgoing_picking.move_lines._is_incoming())
        self.outgoing_picking.move_lines.location_dest_id = self.wh2.lot_stock_id
        self.assertTrue(self.outgoing_picking.move_lines._is_outgoing())
        self.assertTrue(self.outgoing_picking.move_lines._is_incoming())
