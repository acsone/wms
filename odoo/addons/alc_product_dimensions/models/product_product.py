# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    volume_liter = fields.Float(
        digits=(8, 4),
        compute="_compute_volume_liter",
        readonly=True,
        store=False,
        string="Volume (liter)",
        help="Volume in liter",
    )

    # Default unit for Alcyon is cm
    dimensional_uom_id = fields.Many2one(
        readonly=True, default=lambda d: d.env.ref("product.product_uom_cm").id
    )

    @api.depends("volume")
    def _compute_volume_liter(self):
        for rec in self:
            rec.volume_liter = rec.volume * 1000
