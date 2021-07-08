# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    is_blocked_by_picking_policy = fields.Boolean(
        compute="_compute_is_blocked_by_picking_policy"
    )

    @api.depends("move_type", "state", "group_id", "picking_type_subcode")
    def _compute_is_blocked_by_picking_policy(self):
        all_at_once_pickings = self.filtered(
            lambda p: p.move_type == "one" and p.picking_type_subcode
        )
        domain = [
            ("state", "not in", ["assigned", "done", "cancel"]),
            ("move_type", "=", "one"),
            ("picking_type_subcode", "<>", False),
            ("group_id", "in", all_at_once_pickings.mapped("group_id").ids),
        ]
        # if an other picking into the same procurement group and picking_type_subcode
        # is not available, all at once delivery is not possible....
        res = self.read_group(
            domain,
            fields=["group_id", "picking_type_subcode"],
            groupby=["group_id", "picking_type_subcode"],
            lazy=False,
        )
        blocked_group_subcode = {
            (item["group_id"][0], item["picking_type_subcode"]) for item in res
        }
        for rec in self:
            key = (rec.group_id.id, rec.picking_type_subcode)
            rec.is_blocked_by_picking_policy = key in blocked_group_subcode or (
                rec.state not in ["assigned", "done", "cancel"]
                and rec.move_type == "one"
            )
