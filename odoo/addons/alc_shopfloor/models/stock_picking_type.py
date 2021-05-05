# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    shopfloor_menu_ids = fields.Many2many(
        comodel_name="shopfloor.menu", string="Shopfloor Menus", readonly=True,
    )

    @api.constrains("show_entire_packs")
    def _check_move_entire_packages(self):
        menu_items = self.env["shopfloor.menu"].search(
            [("picking_type_ids", "in", self.ids)]
        )
        menu_items._check_move_entire_packages()
