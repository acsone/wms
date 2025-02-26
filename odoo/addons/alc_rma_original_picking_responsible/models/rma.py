# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base.models.res_users import Users
from odoo.addons.rma.models.rma import Rma as RmaBase
from odoo.addons.rma.models.stock_picking import StockPicking


class Rma(RmaBase):

    internal_picking_ids = fields.Many2many[StockPicking](
        compute="_compute_internal_picking_ids",
        string="Preparation Pickings",
        store=True,
    )
    internal_picking_user_ids = fields.Many2many[Users](
        compute="_compute_internal_picking_ids",
        string="Preparation Users",
        store=True,
    )
    internal_picking_id = fields.Many2one[StockPicking](
        compute="_compute_internal_picking_ids",
        string="First Preparation Picking",
        store=True,
    )
    internal_picking_user_id = fields.Many2one[Users](
        compute="_compute_internal_picking_ids",
        string="First Preparation Responsible",
        store=True,
    )

    @api.depends("move_id")
    def _compute_internal_picking_ids(self):
        def _get_chained_moves(move):
            if not move:
                return move
            return move | _get_chained_moves(move.move_orig_ids)

        for rec in self:
            internal_moves = _get_chained_moves(rec.move_id.move_orig_ids)
            pickings = internal_moves.picking_id
            users = pickings.user_id
            rec.internal_picking_ids = pickings
            rec.internal_picking_user_ids = users
            rec.internal_picking_id = pickings[0] if pickings else False
            rec.internal_picking_user_id = users[0] if users else False
