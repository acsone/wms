# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class TestStockReleaseChannelDeliverCommon(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        output_loc = cls.channel.picking_ids.move_ids.location_id
        cls._update_qty_in_location(output_loc, cls.product1, 100)
        cls._update_qty_in_location(output_loc, cls.product2, 100)
        cls.channel.picking_ids.move_ids.write({"procure_method": "make_to_stock"})
        cls.channel.picking_ids.action_assign()
        cls.dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.dock.warehouse_id = cls.wh
        cls.warehouse2 = cls.env.ref("stock.stock_warehouse_shop0")
        cls.channel.dock_id = cls.dock
        cls.channel.action_lock()
        cls.channel.shipment_planning_method = "simple"
        cls.pickings = cls.channel.picking_to_plan_ids
