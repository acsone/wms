# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_id = fields.Many2one(index=True)
    group_id = fields.Many2one(index=True)
