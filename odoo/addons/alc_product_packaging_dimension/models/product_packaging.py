# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    length_cm = fields.Integer(
        "Length (cm)", compute="_compute_length", help="length in centimeters"
    )
    width_cm = fields.Integer(
        "Width (cm)", compute="_compute_width", help="width in centimeters"
    )
    height_cm = fields.Integer(
        "Height (cm)", compute="_compute_height", help="height in centimeters"
    )

    volume_l = fields.Float(
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
        string="Volume (liter)",
        help="Volume in liter",
    )

    @api.depends("lngth")
    def _compute_length(self):
        for pack in self:
            pack.length_cm = pack.lngth / 10.0

    @api.depends("width")
    def _compute_width(self):
        for pack in self:
            pack.width_cm = pack.width / 10.0

    @api.depends("height")
    def _compute_height(self):
        for pack in self:
            pack.height_cm = pack.height / 10.0

    @api.depends("length_cm", "width_cm", "height_cm")
    def _compute_volume(self):
        for pack in self:
            pack.volume_l = (pack.length_cm * pack.width_cm * pack.height_cm) / 1000.0
