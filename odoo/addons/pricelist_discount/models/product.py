# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        """ Check if context contains a price to return instead of product
        prices. Otherwise calls parent method.
        """
        try:
            return self.env.context["override_based_price"]
        except KeyError:
            return super(ProductProduct, self).price_compute(
                price_type=price_type, uom=uom, currency=currency, company=company
            )

    @api.multi
    def _select_seller_for_sale(
        self, partner_id=False, quantity=0.0, date=None, uom_id=False
    ):
        # Copy from _select_seller function
        self.ensure_one()
        if date is None:
            date = fields.Date.today()
        res = self.env["product.supplierinfo"]
        for seller in self.seller_ids:
            # Set quantity in UoM of seller
            quantity_uom_seller = quantity
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(
                    quantity_uom_seller, seller.product_uom
                )

            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                continue
            if quantity_uom_seller < seller.min_qty_sale:
                continue
            if seller.product_id and seller.product_id != self:
                continue

            res |= seller
            break
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        """ Check if context contains a price to return instead of product
        prices. Otherwise calls parent method.
        """
        try:
            return self.env.context["override_based_price"]
        except KeyError:
            return super(ProductTemplate, self).price_compute(
                price_type=price_type, uom=uom, currency=currency, company=company
            )
