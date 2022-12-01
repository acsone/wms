# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields

from odoo.addons.product.models.product_packaging import (
    ProductPackaging as PackagingBase,
)
from odoo.addons.uom.models.uom_uom import UoM


class ProductPackaging(PackagingBase):

    displayed_length = fields.Integer(
        compute="_compute_displayed_length",
        help="length in unit",
        store=True,
        inverse="_inverse_displayed_length",
    )
    displayed_width = fields.Integer(
        compute="_compute_displayed_width",
        help="width in unit",
        store=True,
        inverse="_inverse_displayed_width",
    )
    displayed_height = fields.Integer(
        compute="_compute_displayed_height",
        help="height in unit",
        store=True,
        inverse="_inverse_displayed_height",
    )
    displayed_uom_id = fields.Many2one[UoM](compute="_compute_displayed_uom_id")
    displayed_uom_name = fields.Char(compute="_compute_displayed_uom_id")

    volume_l = fields.Float(
        digits=(8, 4),
        compute="_compute_volume_l",
        readonly=True,
        store=False,
        string="Volume (liter)",
        help="Volume in liter",
    )

    @api.depends_context("company_id")
    @api.depends("length_uom_id")
    def _compute_displayed_uom_id(self):
        # If displayed uom is configured, use that one
        # else, use the one defined on the packaging
        for pack in self:
            displayed_uom_id = (
                self.env.company.packaging_displayed_uom_id
                if self.env.company.packaging_displayed_uom_id
                else pack.length_uom_id
            )
            pack.displayed_uom_id = displayed_uom_id
            pack.displayed_uom_name = displayed_uom_id.display_name

    @api.depends("packaging_length", "length_uom_id", "displayed_uom_id")
    def _compute_displayed_length(self):
        for pack in self:
            pack.displayed_length = pack.length_uom_id._compute_quantity(
                pack.packaging_length, pack.displayed_uom_id
            )

    def _inverse_displayed_length(self):
        for pack in self:
            pack.packaging_length = pack.displayed_uom_id._compute_quantity(
                pack.displayed_length, pack.length_uom_id
            )

    @api.depends("width", "length_uom_id", "displayed_uom_id")
    def _compute_displayed_width(self):
        for pack in self:
            pack.displayed_width = pack.length_uom_id._compute_quantity(
                pack.width, pack.displayed_uom_id
            )

    def _inverse_displayed_width(self):
        for pack in self:
            pack.width = pack.displayed_uom_id._compute_quantity(
                pack.displayed_width, pack.length_uom_id
            )

    @api.depends("height", "length_uom_id", "displayed_uom_id")
    def _compute_displayed_height(self):
        for pack in self:
            pack.displayed_height = pack.length_uom_id._compute_quantity(
                pack.height, pack.displayed_uom_id
            )

    def _inverse_displayed_height(self):
        for pack in self:
            pack.height = pack.displayed_uom_id._compute_quantity(
                pack.displayed_height, pack.length_uom_id
            )

    @api.depends("displayed_length", "displayed_width", "displayed_height")
    def _compute_volume_l(self):
        mm_uom = self.env.ref("uom.product_uom_millimeter")
        for pack in self:
            length = pack.length_uom_id._compute_quantity(pack.displayed_length, mm_uom)
            width = pack.length_uom_id._compute_quantity(pack.displayed_width, mm_uom)
            height = pack.length_uom_id._compute_quantity(pack.displayed_height, mm_uom)
            pack.volume_l = (length * width * height) / 1000.0
