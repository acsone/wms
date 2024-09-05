# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopfloor.tests.test_location_content_transfer_base import (
    LocationContentTransferCommonCase,
)
from odoo.addons.stock_location_orderpoint.tests.common import (
    TestLocationOrderpointCommon,
)


class LocationContentTransferFullCommon(
    LocationContentTransferCommonCase, TestLocationOrderpointCommon
):
    """Tests for Stock Content Transfer in Full Reservation context."""

    @classmethod
    def setUpClassBaseData(cls):
        res = super().setUpClassBaseData()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        # Save user
        user = cls.env.user
        cls.env = cls.env(user=1)
        cls.env.company.restrict_move_line_quantity = True
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        orderpoint, cls.location_src = cls._create_orderpoint_complete(
            "Reserve", trigger="auto"
        )
        cls.reserve_picking_type = orderpoint.route_id.rule_ids.picking_type_id
        cls.reserve_picking_type.merge_move_for_full_location_reservation = True
        # Update shopfloor profile picking types
        cls.menu.sudo().picking_type_ids = orderpoint.route_id.rule_ids.picking_type_id

        cls.reserve = cls.location_src

        cls.location_obj = cls.env["stock.location"]
        cls.location_reserve_1 = cls.location_obj.create(
            {
                "name": "Reserve 1",
                "location_id": cls.location_src.id,
                "barcode": "RESERVE1",
            }
        )
        cls.location_reserve_2 = cls.location_obj.create(
            {
                "name": "Reserve 2",
                "location_id": cls.location_src.id,
                "barcode": "RESERVE2",
            }
        )

        cls._update_qty_in_location(cls.location_reserve_1, cls.product_a, 10)
        cls._update_qty_in_location(cls.location_reserve_2, cls.product_a, 10)

        cls.picking = cls._create_picking(
            picking_type=cls.picking_type_out, lines=[(cls.product_a, 20)]
        )
        cls.picking.picking_type_id.merge_move_for_full_location_reservation = True
        # We don't treat the remaining quantities
        cls.picking.picking_type_id.create_backorder = "never"

        # Reserve quantities
        cls.picking.action_assign()

        cls.env = cls.env(user=user.id)
        return res
