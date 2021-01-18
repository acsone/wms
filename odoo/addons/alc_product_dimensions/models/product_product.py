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
    volume = fields.Float(
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
        string="Volume",
        help="Volume",
    )

    # Default unit for Alcyon is cm
    dimensional_uom_id = fields.Many2one(
        readonly=True, default=lambda d: d.env.ref("product.product_uom_cm").id
    )

    @api.depends("length", "height", "width", "dimensional_uom_id")
    def _compute_volume(self):
        for rec in self:
            if (
                not rec.length
                or not rec.height
                or not rec.width
                or not rec.dimensional_uom_id
            ):
                rec.volume = False
                continue

            length_m = rec.convert_to_meters(rec.length, rec.dimensional_uom_id)
            height_m = rec.convert_to_meters(rec.height, rec.dimensional_uom_id)
            width_m = rec.convert_to_meters(rec.width, rec.dimensional_uom_id)
            rec.volume = length_m * height_m * width_m

    @api.depends("volume")
    def _compute_volume_liter(self):
        for rec in self:
            rec.volume_liter = rec.volume * 1000
