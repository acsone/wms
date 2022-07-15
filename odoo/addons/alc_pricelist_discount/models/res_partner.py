# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    discount_pricelist_ids = fields.Many2many(domain=[("is_discount", "=", True)])
    property_product_pricelist = fields.Many2one(domain=[("is_discount", "=", False)])

    @api.constrains("property_product_pricelist", "discount_pricelist_ids")
    def _constrain_discount_pricelists(self):
        if not self.env["product.pricelist"].enforce_discount_constraint():
            return
        if any(self.mapped("property_product_pricelist.is_discount")):
            msg = _("Some partners have a discount pricelist set as base pricelist.")
            raise ValidationError(msg)
        # in version 10, verifying constraint on many2many doesn't work,
        # because __set__ does:
        #     record.write({self.name: write_value})
        #     env.cache[self][record.id] = value
        # in that order.
        # Which means during the write that triggers the constraint,
        # the value is not set yet so the constraint is not actually checked.
        # in case we directly do a write, same problem, the cache is not set.
        # As a result, we need to check in SQL...
        query = """
            SELECT partner_id
            FROM partner_discount_pricelist_rel rel
            JOIN product_pricelist pl on pl.id = rel.pricelist_id
            WHERE pl.is_discount = False
        """
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        if res:
            msg = _("Some partners have a base pricelist set as discount pricelist.")
            raise ValidationError(msg)
