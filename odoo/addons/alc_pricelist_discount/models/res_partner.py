# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.alc_partner_pricelist.models import ResPartner as BaseResPartner

from .product_pricelist import ProductPricelist


class ResPartner(BaseResPartner):

    discount_pricelist_ids = fields.Many2many[ProductPricelist](
        domain=[("is_discount", "=", True)]
    )
    property_product_pricelist = fields.Many2one[ProductPricelist](
        domain=[("is_discount", "=", False)]
    )

    @api.constrains("property_product_pricelist", "discount_pricelist_ids")
    def _constrain_discount_pricelists(self):
        if not self.env["product.pricelist"].enforce_discount_constraint():
            return
        if any(self.mapped("property_product_pricelist.is_discount")):
            msg = _("Some partners have a discount pricelist set as base pricelist.")
            raise ValidationError(msg)
        if not all(self.mapped("discount_pricelist_ids.is_discount")):
            raise ValidationError(
                _("Some partners have a base pricelist set as discount pricelist.")
            )
