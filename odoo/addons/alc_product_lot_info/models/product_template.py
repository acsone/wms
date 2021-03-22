# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    lot_ids = fields.One2many(
        "stock.production.lot", string="Lots", compute="_compute_lot_ids"
    )

    def _compute_lot_ids(self):
        for rec in self:
            lot_ids = rec.mapped("product_variant_ids.lot_ids")

            rec.lot_ids = lot_ids.sorted(
                key=lambda l: (l.qty_available, l.life_date), reverse=True
            )
