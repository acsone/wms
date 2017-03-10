# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    promotion_pricelist_id = fields.Many2one(
        string='Supplier Promotion Pricelist',
        comodel_name='product.pricelist',
        company_dependent=True,
    )

    discount_pricelist_id = fields.Many2one(
        string='Alcyon Discount Pricelist',
        comodel_name='product.pricelist',
        company_dependent=True,
    )

    @api.model
    def _commercial_fields(self):
        """ Adds both new pricelists as commercial fields so
        theirs values will be synced to children partners.
        """
        return (
            super(ResPartner, self)._commercial_fields() +
            ['promotion_pricelist_id', 'discount_pricelist_id']
        )
