# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_promotion_sale_allowed = fields.Boolean(
        string="Supplier promotion allowed on sale"
    )

    discount_pricelist_ids = fields.Many2many(
        "product.pricelist",
        "partner_discount_pricelist_rel",
        "partner_id",
        "pricelist_id",
        string="Alcyon Discount Pricelist",
    )

    @api.model
    def _commercial_fields(self):
        """ Adds fields as commercial fields so
        theirs values will be synced to children partners.
        """
        return super(ResPartner, self)._commercial_fields() + [
            "supplier_promotion_sale_allowed",
            "discount_pricelist_ids",
        ]
