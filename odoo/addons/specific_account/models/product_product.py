# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_partner_ref(self):
        """ Called from invoice product onchange.
        As there is a column with product code on the SO/invoice, do not
        put internal code prefix on the line description. This rule applies for
        SO and Invoice at product onchange as invoice line description is
        copied from SO line description. """
        if self.env.context.get('type') in ('out_invoice', 'out_refund'):
            self.partner_ref = self.name
        else:
            super(ProductProduct, self)._compute_partner_ref()
