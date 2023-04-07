# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock_picking_start.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def action_start(self):
        res = super().action_start()
        channel_picking_type_todo = self._get_release_channel_auto_allow_pick_needed(
            "auto_disallow_pick"
        )
        for channel, picking_type in channel_picking_type_todo:
            channel._set_pick_allowed(pick_allowed=False, picking_type=picking_type)
        return res

    def _action_done(self):
        res = super()._action_done()
        channel_picking_type_todo = self._get_release_channel_auto_allow_pick_needed(
            "auto_allow_pick"
        )
        for channel, picking_type in channel_picking_type_todo:
            channel.with_delay(eta=channel.auto_allow_pick_datetime)._set_pick_allowed(
                pick_allowed=True, picking_type=picking_type
            )
        return res

    def _get_release_channel_auto_allow_pick_needed(self, action):
        channel_picking_type_todo = []
        picking_types_allowing_pick = self.env["stock.picking.type"].search(
            [("release_channel_can_allow_pick", "=", True)]
        )
        for rec in self:
            channel_picking_type = (rec.release_channel_id, rec.picking_type_id)
            if channel_picking_type in channel_picking_type_todo:
                continue
            if rec._check_release_channel_auto_allow_pick_needed(action):
                if rec.picking_type_id not in picking_types_allowing_pick:
                    # this picking type is not set to be managed individually for
                    # pick_allowed aspect, we return only the channel to disallow pick
                    # for it
                    channel_picking_type_todo.append((rec.release_channel_id, None))
                else:
                    channel_picking_type_todo.append(
                        (rec.release_channel_id, rec.picking_type_id)
                    )
        return channel_picking_type_todo

    def _check_release_channel_auto_allow_pick_needed(self, action):
        self.ensure_one()
        if not self.release_channel_id or not self.release_channel_id[action]:
            return False
        if action == "auto_allow_pick":
            pickings = self.release_channel_id.picking_ids
            if pickings.filtered(
                lambda p, pt=self.picking_type_id: p.state not in ("cancel", "done")
                and p.picking_type_id == pt
            ):
                return False
        return True
