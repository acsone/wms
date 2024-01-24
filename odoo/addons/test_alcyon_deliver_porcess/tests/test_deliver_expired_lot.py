# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestDeliverProcessBase


class TestDeliverExpiredLot(TestDeliverProcessBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=False))
        cls.channel = cls.channel.with_context(queue_job__no_delay=False)
        cls.product1 = cls.env["product.product"].create(
            {"name": "product1", "tracking": "lot", "type": "product"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "product1", "tracking": "lot", "type": "product"}
        )
        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "lot",
                "product_id": cls.product1.id,
                "expiration_date": "2023-01-01",
            }
        )
        cls.lot2 = cls.env["stock.lot"].create(
            {"name": "lot", "product_id": cls.product2.id}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product1, cls.loc_stock, 3, lot_id=cls.lot1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product2, cls.loc_stock, 3, lot_id=cls.lot2
        )

    def _create_and_release_so(self, **kwargs):
        with trap_jobs() as trap_so:
            sale = self._confirm_sale_order(**kwargs)
            with trap_jobs() as trap_pick:
                trap_so.perform_enqueued_jobs()
                trap_pick.perform_enqueued_jobs()
        return sale

    def test_00(self):
        """Test backorder unreleased after deliver an assigned to release channel at wakeup."""
        self.channel.action_unlock()
        sale1 = self._create_and_release_so(
            products=[self.product1, self.product2], qty=2
        )
        sale2 = self._create_and_release_so(
            products=[self.product2], qty=1, partner=self.partner2
        )
        ship1 = self._get_picking_ship(sale1)
        ship2 = self._get_picking_ship(sale2)
        pick1 = self._get_picking_pick(sale1)
        pick2 = self._get_picking_pick(sale2)

        # do the pick
        pick1._put_in_pack(pick1.move_line_ids)
        pick1.action_set_quantities_to_reservation()
        pick1.move_line_ids.filtered(
            lambda l: l.product_id == self.product2
        ).qty_done -= 1
        pick1._action_done()
        pick2._put_in_pack(pick2.move_line_ids)
        pick2.action_set_quantities_to_reservation()
        pick2._action_done()
        self.assertEqual(pick1.state, "done")
        self.assertEqual(pick2.state, "done")
        # deliver the release channel
        self.channel.action_lock()
        with trap_jobs() as trap_rc:
            self.channel.action_delivering()
            self.assertEqual(self.channel.state, "delivering")
            with trap_jobs() as trap_sa:
                trap_rc.perform_enqueued_jobs()
                advices = self.channel.shipment_advice_ids.filtered(
                    lambda s: s.state not in ("done", "cancel")
                )
                with trap_jobs() as trap_sap:
                    # picking jobs
                    trap_sa.perform_enqueued_jobs()
                    trap_sap.perform_enqueued_jobs()
        self.assertEqual(ship1.state, "assigned")
        self.assertEqual(ship2.state, "done")
        self.assertEqual(advices.state, "error")
        self.assertEqual(self.channel.state, "delivering_error")
