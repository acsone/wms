# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):

    pick_allowed = fields.Boolean(default=True)
    pick_allowed_by_picking_type = fields.Json()
    auto_disallow_pick = fields.Boolean(
        string="Disallow picking automatically",
        help="Disallow picking automatically after ongoing transfers are started",
    )
    auto_allow_pick = fields.Boolean(
        string="Allow picking automatically",
        help="Allow picking automatically after all ongoing transfers are done",
    )
    auto_allow_pick_after = fields.Float(
        "Allow picking automatically after", default=0.5
    )

    def button_toggle_pick_allowed(self):
        if self.env.context.get("picking_type_id"):
            self._toggle_pick_allowed_for_picking_type_id(
                self.env.context.get("picking_type_id")
            )
        else:
            self._toggle_pick_allowed_channel()

    def _toggle_pick_allowed_channel(self):
        started = self.filtered("pick_allowed")
        stopped = self - started
        started.write({"pick_allowed": False, "pick_allowed_by_picking_type": False})
        stopped.write({"pick_allowed": True, "pick_allowed_by_picking_type": False})

    def _toggle_pick_allowed_for_picking_type_id(self, picking_type_id: int):
        for rec in self:
            pick_allowed_by_picking_type = (
                dict(rec.pick_allowed_by_picking_type)
                if rec.pick_allowed_by_picking_type
                else {}
            )
            pick_allowed = rec._get_picking_type_pick_allowed(picking_type_id)
            pick_allowed_by_picking_type.update({picking_type_id: not pick_allowed})
            rec.pick_allowed_by_picking_type = pick_allowed_by_picking_type

    def _set_pick_allowed(self, pick_allowed: bool, picking_type=None):
        if picking_type:
            return self._set_pick_allowed_for_picking_type_id(
                picking_type.id, pick_allowed
            )
        self.write({"pick_allowed": pick_allowed})
        return True

    def _set_pick_allowed_for_picking_type_id(
        self, picking_type_id: int, pick_allowed: bool
    ):
        for rec in self:
            pick_allowed_by_picking_type = (
                dict(rec.pick_allowed_by_picking_type)
                if rec.pick_allowed_by_picking_type
                else {}
            )
            pick_allowed_by_picking_type.update({picking_type_id: pick_allowed})
            rec.pick_allowed_by_picking_type = pick_allowed_by_picking_type

    def _get_picking_type_pick_allowed(self, picking_type_id: int):
        self.ensure_one()
        if isinstance(picking_type_id, int):
            picking_type_id = str(picking_type_id)
        if (
            not self.pick_allowed_by_picking_type
            or picking_type_id not in self.pick_allowed_by_picking_type
        ):
            return self.pick_allowed
        return self.pick_allowed_by_picking_type.get(picking_type_id)

    def _get_all_picking_type_ids_pick_allowed(self):
        """For a release channel return all picking types where pick is allowed."""
        self.ensure_one()
        res = []
        for picking_type in self.env["stock.picking.type"].search(
            [("release_channel_can_allow_pick", "=", True)]
        ):
            if self._get_picking_type_pick_allowed(picking_type_id=picking_type.id):
                res.append(picking_type.id)
        return res
