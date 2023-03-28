# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_put_in_pack_done = fields.Boolean("Put in Pack done", default=False)

    @api.multi
    def _create_lots_for_picking(self):
        return super(
            StockPicking, self.with_context(default_life_date_allowed=True)
        )._create_lots_for_picking()
