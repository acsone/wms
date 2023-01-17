# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_compare


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _get_applicable_pricelist_item(self, date, quantity, pricelists=None):
        self.ensure_one()
        if not pricelists:
            pricelists = self.env["product.pricelist"].search([])
        rules = self.env["product.pricelist.item"]
        for pricelist in pricelists:
            for rule in pricelist._get_applicable_rules(self, date):
                if not rule._is_applicable_for(self, quantity):
                    continue
                rules |= rule
        return rules

    def _get_best_applicable_pricelist_item(self, date, quantity, pricelists, currency):
        if not self:
            return False
        self.ensure_one()
        price_by_rule = {
            rule.id: rule._compute_price(
                self, quantity, self.uom_id, date, currency=currency
            )
            for rule in self._get_applicable_pricelist_item(date, quantity, pricelists)
        }
        if not price_by_rule:
            return False
        return min(price_by_rule.items(), key=lambda item: item[1])[0]

    def _select_seller(
        self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False
    ):
        # FIXME: Copy from _select_seller function, find better way
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        res = self.env["product.supplierinfo"]
        sellers = self.seller_ids
        sellers = sellers.filtered(
            lambda s: not s.company_id or s.company_id.id == self.env.company.id
        )
        for seller in sellers:
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
            if partner_id and seller.partner_id not in [
                partner_id,
                partner_id.parent_id,
            ]:
                continue
            if (
                quantity is not None
                and float_compare(
                    quantity_uom_seller, seller.min_qty, precision_digits=precision
                )
                == -1
            ):
                continue
            if quantity_uom_seller < seller.min_qty_sale:
                continue
            if seller.product_id and seller.product_id != self:
                continue
            if not res or res.partner_id == seller.partner_id:
                res |= seller
        return res.sorted("price")[:1]
