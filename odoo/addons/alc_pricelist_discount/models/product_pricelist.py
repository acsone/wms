# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    is_discount = fields.Boolean(default=False)

    @api.constrains("is_discount")
    def _constrain_is_discount(self):
        # since is_discount usages are exclusive, that means that if the pricelist
        # is used somewhere, you cannot change its value.
        field = self.env.ref("product.field_res_partner_property_product_pricelist")
        msg = _("You cannot change a pricelist that is already in use.")
        for pricelist in self:
            if pricelist.is_discount:
                domain_pricelist = [
                    ("fields_id", "=", field.id),
                    ("value_reference", "=", "product.pricelist,%s" % pricelist.id),
                ]
                if self.env["ir.property"].search(domain_pricelist, limit=1):
                    raise ValidationError(msg)
            else:
                domain_partners = [("discount_pricelist_id", "=", pricelist.id)]
                if self.env["res.partner"].search(domain_partners, limit=1):
                    raise ValidationError(msg)
