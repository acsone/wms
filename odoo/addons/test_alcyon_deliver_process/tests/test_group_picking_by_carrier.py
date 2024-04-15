# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestDeliverProcessBase


class TestGroupPickingByCarrier(TestDeliverProcessBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel1 = cls.channel
        cls.channel2 = cls.env["stock.release.channel"].create(
            {
                "name": "Release Channel",
                "release_mode": "auto",
                "state": "locked",
                "shipment_planning_method": "simple",
                "partner_ids": [Command.set(cls.partner1.ids)],
                "warehouse_id": cls.warehouse_1.id,
                "dock_id": cls.dock.id,
            }
        )
        cls.carrier1 = cls.env.ref("delivery.delivery_carrier")
        cls.carrier2 = cls.env.ref("delivery.delivery_local_delivery")
        cls.channel1.carrier_ids = cls.carrier1
        cls.channel2.carrier_ids = cls.carrier2
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "tracking": "none", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 100.0
        )

    def test_0(self):
        self.warehouse_1.route_ids.rule_ids.propagate_carrier = True
        sale1 = self._confirm_sale_order(
            products=[self.product], qty=2, carrier_id=self.carrier1.id
        )
        sale2 = self._confirm_sale_order(
            products=[self.product], qty=2, carrier_id=self.carrier2.id
        )

        with trap_jobs() as trap:
            self.channel1.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()

        with trap_jobs() as trap:
            self.channel2.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()

        ship1 = self._get_picking_ship(sale1)
        pick1 = self._get_picking_pick(sale1)
        self.assertEqual(len(ship1), 1)
        self.assertEqual(len(pick1), 1)
        self.assertEqual(ship1.carrier_id, self.carrier1)
        self.assertEqual(ship1.release_channel_id, self.channel1)
        self.assertEqual(pick1.release_channel_id, self.channel1)

        ship2 = self._get_picking_ship(sale2)
        pick2 = self._get_picking_pick(sale2)
        self.assertEqual(len(ship2), 1)
        self.assertEqual(len(pick2), 1)
        self.assertEqual(ship2.carrier_id, self.carrier2)
        self.assertEqual(ship2.release_channel_id, self.channel2)
        self.assertEqual(pick2.release_channel_id, self.channel2)

        self.assertEqual(pick1.state, "assigned")
        self.assertEqual(pick2.state, "assigned")
        self.assertFalse(pick1 == pick2)
