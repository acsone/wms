# -*- coding: utf-8 -*-
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    additional_move_id = fields.Many2one(
        "stock.move",
        "Additional Product Move",
        ondelete="set null",
        index=True,
        old="additional_move",
    )
