# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.alc_additional_product_stock.tests.common import StockPickingTestCase


class TestDeliverProcessBase(StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.env.user.company_id.shipment_advice_run_in_queue_job = True
        cls.env["stock.release.channel"].search([]).unlink()
        cls.dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.partner2 = cls.env["res.partner"].create({"name": "partner 2"})
        cls.channel = cls.env["stock.release.channel"].create(
            {
                "name": "Release Channel",
                "release_mode": "auto",
                "state": "locked",
                "shipment_planning_method": "simple",
                "partner_ids": [Command.set((cls.partner1 | cls.partner2).ids)],
                "warehouse_id": cls.warehouse_1.id,
                "dock_id": cls.dock.id,
            }
        )
        cls.warehouse_1.route_ids.available_to_promise_defer_pull = True
        cls.warehouse_1.out_type_id.propagate_to_pickings_chain = True
        cls.warehouse_1.out_type_id.no_backorder_for_additional_product = True
        cls.warehouse_1.out_type_id.group_pickings_by_customer = True
        cls.warehouse_1.out_type_id.group_pickings = True
        cls.warehouse_1.pick_type_id.no_backorder_for_additional_product = True
