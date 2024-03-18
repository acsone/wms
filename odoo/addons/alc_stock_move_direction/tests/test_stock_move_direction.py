# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.stock.models.stock_picking import Picking


class TestStockMoveDirection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Code product",
            }
        )

        wh = cls.env["stock.warehouse"].search([], limit=1)
        cls.wh = wh
        cls.wh2 = wh.copy({"name": "wh2", "code": "wh2_code"})
        cls.pick_type_in = cls.env.ref("stock.picking_type_out")
        cls.pick_type_out = cls.env.ref("stock.picking_type_in")
        cls.pick_type_int = cls.env.ref("stock.picking_type_internal")

        cls.ResPartner = cls.env["res.partner"]
        cls.supplier = cls.ResPartner.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )
        cls.customer = cls.ResPartner.create(
            {"name": "Unittest customer", "ref": "abc"}
        )
        cls.stock_location = wh.view_location_id
        cls.lot_stock_id = wh.lot_stock_id
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.StockLocation = cls.env["stock.location"]
        cls.reception_location = cls.StockLocation.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "internal",
            }
        )
        cls.bin1 = cls.StockLocation.create(
            {
                "name": "bin1",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        cls._change_product_qty(cls.product, cls.bin1, 10)
        cls.StockLocation._parent_store_compute()
        cls.StockPicking = cls.env["stock.picking"]
        picking = cls.StockPicking.create(
            {
                "picking_type_id": cls.pick_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_ids": [
                    Command.create(
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
                "move_ids": [
                    Command.create(
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

        picking: Picking = cls.StockPicking.create(
            {
                "picking_type_id": cls.pick_type_int.id,
                "location_id": cls.reception_location.id,
                "location_dest_id": cls.lot_stock_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "move 1",
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.reception_location.id,
                            "location_dest_id": cls.lot_stock_id.id,
                        },
                    )
                    for product in cls.product
                ],
            }
        )
        cls.replenishment_picking = picking.with_context(test_mode=1)

    @classmethod
    def _change_product_qty(cls, product, location, qty):
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "inventory_quantity": qty,
            }
        )._apply_inventory()

    def test_incoming_move(self):
        # here we have a move from seller to reception under stock
        self.assertTrue(self.incoming_picking.move_ids._is_incoming())
        # once the picking is  condirmerd, the check is done on the pack_operation
        self.incoming_picking.action_assign()
        self.assertTrue(self.incoming_picking.move_ids._is_incoming())
        # if I set a location dest into the pack not under stock
        # this one us used into the compute
        self.incoming_picking.move_ids.move_line_ids.location_dest_id = (
            self.customer_location
        )
        self.assertFalse(self.incoming_picking.move_ids._is_incoming())
        # if we have no pack operation, the destination on move is used to know
        # if the picking is incoming
        self.incoming_picking.move_ids.move_line_ids.unlink()
        self.assertTrue(self.incoming_picking.move_ids._is_incoming())

    def test_stock_replenish_move(self):
        # here we have a move from seller to reception under stock
        self.assertTrue(self.replenishment_picking.move_ids._is_stock_replenishment())
        self.replenishment_picking.action_assign()
        # if I set a location dest into the pack not under stock
        # this one us used into the compute
        self.replenishment_picking.move_ids.move_line_ids.location_dest_id = (
            self.customer_location
        )
        self.assertFalse(self.replenishment_picking.move_ids._is_stock_replenishment())
        # if we have no pack operation, the destination on move is used to know
        # if the picking is incoming
        self.replenishment_picking.move_ids.move_line_ids.unlink()
        self.assertTrue(self.replenishment_picking.move_ids._is_stock_replenishment())

    def test_outgoing_move(self):
        # here we have a move from stock to customer
        self.assertTrue(self.outgoing_picking.move_ids._is_outgoing())
        # once the picking is  condirmerd, the check is done on the pack_operation
        self.outgoing_picking.action_assign()
        self.assertTrue(self.outgoing_picking.move_ids._is_outgoing())
        # if I set a location dest into the pack not under stock
        # this one us used into the compute
        self.outgoing_picking.move_ids.move_line_ids.location_dest_id = (
            self.stock_location.id
        )
        self.assertFalse(self.outgoing_picking.move_ids._is_outgoing())
        # if we have no pack operation, the destination on move is used to know
        # if the picking is outgoing
        self.outgoing_picking.move_ids.move_line_ids.unlink()
        self.assertTrue(self.outgoing_picking.move_ids._is_outgoing())

    def test_wh_transfer_move(self):
        # in this case: origin and dest are 2 locations under a stock location
        # but into different warehouses
        self.assertTrue(self.outgoing_picking.move_ids._is_outgoing())
        self.assertFalse(self.outgoing_picking.move_ids._is_incoming())
        self.outgoing_picking.move_ids.location_dest_id = self.wh2.lot_stock_id
        self.assertTrue(self.outgoing_picking.move_ids._is_outgoing())
        self.assertTrue(self.outgoing_picking.move_ids._is_incoming())

    def _get_cached_stock_locations_boundaries(self):
        warehouse_model = self.env["stock.warehouse"]
        cache = warehouse_model.pool._Registry__cache.d
        for model_name, f, *_args in cache.keys():
            if (
                model_name == warehouse_model._name
                and f.__name__ == "_get_stock_locations_boundaries"
            ):
                return cache.get((model_name, f))
        return None

    def test_stock_locations_boundaries_cache(self):
        warehouse_model = self.env["stock.warehouse"]
        warehouse_model._get_stock_locations_boundaries.clear_cache(warehouse_model)
        self.assertFalse(self._get_cached_stock_locations_boundaries())
        res = self.wh._get_stock_locations_boundaries()
        self.assertDictEqual(res, self._get_cached_stock_locations_boundaries())
        new_parent_location = self.stock_location.location_id.copy()
        self.wh.view_location_id.location_id = new_parent_location
        self.assertFalse(self._get_cached_stock_locations_boundaries())
        self.wh._get_stock_locations_boundaries()
        cached_res = self._get_cached_stock_locations_boundaries()
        self.assertEqual(
            cached_res.get(self.stock_location.id), self.stock_location.parent_path
        )
