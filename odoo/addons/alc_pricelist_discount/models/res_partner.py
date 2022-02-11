# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    discount_pricelist_id = fields.Many2one(domain=[("is_discount", "=", True)])
    property_product_pricelist = fields.Many2one(domain=[("is_discount", "=", False)])

    @api.constrains("property_product_pricelist", "discount_pricelist_id")
    def _constrain_discount_pricelists(self):
        if not self.env["product.pricelist"].enforce_discount_constraint():
            return
        if any(self.mapped("property_product_pricelist.is_discount")):
            msg = _("Some partners have a discount pricelist set as base pricelist.")
            raise ValidationError(msg)
        if not all(self.mapped("discount_pricelist_id.is_discount")):
            msg = _("Some partners have a base pricelist set as discount pricelist.")
            raise ValidationError(msg)
