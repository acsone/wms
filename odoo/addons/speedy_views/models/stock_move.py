# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    procurement_id = fields.Many2one(index=True)
    split_from = fields.Many2one(index=True)
    origin_returned_move_id = fields.Many2one(index=True)
    inventory_id = fields.Many2one(index=True)
