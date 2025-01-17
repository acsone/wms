# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_product import ProductProduct as ProductBase
from odoo.addons.uom.models.uom_uom import UoM


class ProductProduct(ProductBase):

    product_length = fields.Float(copy=False)
    product_height = fields.Float(copy=False)
    product_width = fields.Float(copy=False)
    product_weight = fields.Float(copy=False)

    volume_liter = fields.Float(
        digits=(8, 4),
        compute="_compute_volume_liter",
        readonly=True,
        store=False,
        string="Volume (liter)",
        help="Volume in liter",
    )

    # Default unit for Alcyon is cm
    dimensional_uom_id = fields.Many2one[UoM](
        default=lambda d: d.env.ref("uom.product_uom_cm").id, readonly=True
    )

    @api.depends("volume")
    def _compute_volume_liter(self) -> None:
        """
        As volume is always expressed in m³, the liter volume.

        does not depends on dimensional uom
        """
        for rec in self:
            rec.volume_liter = rec.volume * 1000
