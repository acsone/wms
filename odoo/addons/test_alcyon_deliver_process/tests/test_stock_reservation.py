# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestDeliverProcessBase


class TestPartialDeliver(TestDeliverProcessBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "tracking": "none", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.loc_stock, 3)
        cls.lot = cls.env["stock.lot"].create(
            {"name": "lot", "product_id": cls.product.id}
        )
        cls.lot2 = cls.env["stock.lot"].create(
            {"name": "lot2", "product_id": cls.product.id}
        )

    def test_00(self):
        """Manual change of reserved lot shouldn't lead to a negative stock."""
        self.product.stock_quant_ids.unlink()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, 1, lot_id=self.lot
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, 1, lot_id=self.lot2
        )
        sale = self._confirm_sale_order(products=[self.product], qty=1)
        sale2 = self._confirm_sale_order(
            products=[self.product], qty=1, partner=self.partner2
        )
        # open the channel, pick must be generated
        with trap_jobs() as trap:
            self.channel.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, -1, lot_id=self.lot
        )
        picks = self._get_picking_pick(sale) | self._get_picking_pick(sale2)
        pick1 = picks.filtered(lambda p: p.move_line_ids.lot_id == self.lot)
        pick2 = picks.filtered(lambda p: p.move_line_ids.lot_id == self.lot2)
        self.assertEqual(pick1.move_line_ids.reserved_uom_qty, 1)
        self.assertEqual(pick2.move_line_ids.reserved_uom_qty, 1)
        pick1.move_line_ids.lot_id = self.lot2
        pick1.move_line_ids.qty_done = 1
        self.assertEqual(pick1.move_line_ids.reserved_uom_qty, 1)
        pick2.move_line_ids.qty_done = 1
        picks._action_done()
        self.assertEqual(pick1.state, "done")
        self.assertEqual(pick2.state, "confirmed")
        ships = self._get_picking_ship(sale) | self._get_picking_ship(sale2)
        self.assertEqual(sum(self.lot2.quant_ids.mapped("quantity")), 1)
        self.assertEqual(sum(self.lot2.quant_ids.mapped("reserved_quantity")), 1)
        self.channel.action_lock()
        self.channel.unrelease_picking()
        self.channel.action_deliver()
        self.assertSetEqual(set(ships.mapped("state")), {"waiting", "done"})
        self.assertEqual(pick2.state, "cancel")
        self.assertEqual(self.lot2.qty_available, 0)
