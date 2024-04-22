# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.stock_location_orderpoint.tests.common import (
    TestLocationOrderpointCommon,
)


class TestLocationOrderpointPriority(TestLocationOrderpointCommon):
    def test_auto_replenishment(self):
        """
        First, use an automatic orderpoint as:

        - Creating a product quantity on replenishment source
        - Creating an outgoing move
        - A first replenishment move is created with priority == 0
        - Unlink the orderpoint (to avoid sql constraint)
        - Add a manual orderpoint with priority == 1
        - Create an outgoing move
        - Run the orderpoint
        - The existing move should have changed its priority to 1
        """
        job_func = self.env["stock.location.orderpoint"].run_auto_replenishment
        move_qty = 12
        move = self._create_outgoing_move(move_qty)
        orderpoint, location_src = self._create_orderpoint_complete(
            "Stock2", trigger="auto"
        )

        with trap_jobs() as trap:
            move = self._create_incoming_move(50, location_src)
            trap.assert_jobs_count(1, only=job_func)
            trap.assert_enqueued_job(
                orderpoint.browse([]).run_auto_replenishment,
                args=(move.product_id, move.location_dest_id, "location_src_id"),
                kwargs={},
                properties={
                    "identity_key": identity_exact,
                },
            )
            self.product.invalidate_recordset()
            trap.perform_enqueued_jobs()
            replenish_move_1 = self._get_replenishment_move(orderpoint)
            self._assert_replenishment_move(replenish_move_1, move_qty, orderpoint)
        self.assertEqual(replenish_move_1.priority, "0")
        values = {"trigger": "manual"}
        orderpoint_manual_data = orderpoint.copy_data(values)
        # As only one orderpoint with same replenish method
        orderpoint.unlink()
        orderpoint_manual = self.env["stock.location.orderpoint"].create(
            orderpoint_manual_data
        )
        orderpoint_manual.priority = "1"
        move = self._create_outgoing_move(move_qty)
        self._run_replenishment(orderpoint_manual)
        self.assertEqual(replenish_move_1.product_uom_qty, 24)
        self.assertEqual(replenish_move_1.priority, "1")
