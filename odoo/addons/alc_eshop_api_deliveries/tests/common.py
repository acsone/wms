# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import deliveries_router


class TestDeliveriesService(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.default_fastapi_router = deliveries_router
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.product_ship = cls.env["product.product"].create(
            {"name": "Shipit", "default_code": "SHP"}
        )
        cls.product_cancel = cls.env["product.product"].create(
            {"name": "Cancel", "default_code": "CNL"}
        )

        cls.location_customer = cls.env.ref("stock.stock_location_customers")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

        moves_picking_cancel = [(cls.product_cancel, 1)]
        moves_picking_done = [(cls.product_ship, 1)]
        cls.picking_cancel = cls.create_picking(moves_picking_cancel)
        cls.picking_half = cls.create_picking(moves_picking_cancel + moves_picking_done)
        cls.picking_done = cls.create_picking(moves_picking_done)

        cls.picking_cancel.with_context(force_cancel=True).action_cancel()
        # picking_half: cancel half of it, deliver the rest
        def filter_move(m):
            return m.product_id == cls.product_cancel

        cls.move_done_cancel = cls.picking_half.move_ids.filtered(filter_move)
        cls.move_done_cancel.state = "cancel"
        cls.picking_half.action_confirm()
        for move in cls.picking_half.move_ids - cls.move_done_cancel:
            move.quantity_done = move.product_uom_qty
        cls.picking_half._action_done()

        cls.picking_done.action_confirm()
        for move in cls.picking_done.move_ids:
            move.quantity_done = move.product_uom_qty
        cls.picking_done._action_done()

    @classmethod
    def create_picking(cls, move_tuples, partner=None):
        moves = []
        for product, qty in move_tuples:
            move = {
                "name": f"{product.name} {qty}",
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": cls.location_stock.id,
                "location_dest_id": cls.location_customer.id,
            }
            moves.append((0, 0, move))
        vals = {
            "picking_type_id": cls.picking_type_out.id,
            "location_id": cls.location_stock.id,
            "location_dest_id": cls.location_customer.id,
            "partner_id": (partner or cls.partner).id,
            "customer_id": (partner or cls.partner).id,
            "move_ids": moves,
        }
        return cls.env["stock.picking"].create(vals)
