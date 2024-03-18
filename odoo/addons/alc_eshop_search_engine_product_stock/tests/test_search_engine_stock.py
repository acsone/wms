# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader_search_engine_product_stock.tests.common import (
    StockCommonCase,
)
from odoo.addons.stock.models.stock_move import StockMove


class TestSearchEngineProductStock(StockCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=False))
        wh = cls.env["stock.warehouse"].search([], limit=1)
        cls.wh = wh
        cls.pick_type_in = cls.env.ref("stock.picking_type_out")
        cls.pick_type_out = cls.env.ref("stock.picking_type_in")
        cls.pick_type_int = cls.env.ref("stock.picking_type_internal")

        cls.view_location = wh.view_location_id
        cls.lot_stock_id = wh.lot_stock_id
        cls.reception_location = cls.env["stock.location"].create(
            {
                "name": "reception",
                "location_id": cls.view_location.id,
                "usage": "internal",
            }
        )

        cls.picking_type_in.default_location_dest_id = cls.reception_location

    def _create_replenishment_move(self) -> StockMove:

        return self.env["stock.move"].create(
            {
                "name": "Forced Move",
                "location_id": self.reception_location.id,
                "location_dest_id": self.lot_stock_id.id,
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "product_uom": self.product.uom_id.id,
                "picking_type_id": self.pick_type_int.id,
            }
        )

    def test_incoming_move_replenish(self):
        """
        The incoming move should generate an stock update.

        as a replenishment move.
        """
        job = self.job_counter()
        move = self._create_incoming_move()
        move._action_confirm()
        self.assertEqual(job.count_created(), 1)

        job = self.job_counter()
        job.existing.button_done()
        move = self._create_replenishment_move()
        move._action_confirm()
        self.assertEqual(job.count_created(), 1)
