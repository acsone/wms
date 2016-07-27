# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


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

    def _commercial_fields(self, cr, uid, context=None):
        """ Adds both new pricelists as commercial fields so
        theirs values will be synced to children partners.
        """
        return super(ResPartner, self)._commercial_fields(
            cr, uid, context=context
        ) + ['promotion_pricelist_id', 'discount_pricelist_id']
