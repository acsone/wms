# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError
from odoo.tools import ormcache

from odoo.addons.product.models.product_pricelist import Pricelist


class ProductPricelist(Pricelist):

    is_discount = fields.Boolean(default=False)

    @api.model
    @ormcache()
    def enforce_discount_constraint(self):
        key = "constrain_discount_pricelist"
        value = self.env["ir.config_parameter"].sudo().get_param(key, "").lower()
        return value in ["true", "1", "t", "y", "yes"]

    @api.constrains("is_discount")
    def _constrain_is_discount(self):
        """
        Since is_discount usages are exclusive, that means that if the pricelist.

        is used somewhere, you cannot change its value.
        """
        if not self.enforce_discount_constraint():
            return
        msg = _("You cannot change a pricelist that is already in use.")
        property_model = self.env["ir.property"]
        partner_model = self.env["res.partner"]
        for rec in self:
            if rec.is_discount:
                if property_model.search(
                    [
                        ("name", "=", "property_product_pricelist"),
                        ("res_id", "like", "res.partner%"),
                        ("value_reference", "=", f"product.pricelist,{rec.id}"),
                    ],
                    limit=1,
                ):
                    raise ValidationError(msg)
            else:
                if partner_model.search(
                    [("discount_pricelist_ids", "in", rec.id)], limit=1
                ):
                    raise ValidationError(msg)
