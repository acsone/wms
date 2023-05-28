# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
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

    def _get_best_applicable_pricelist_item_id(
        self, date, quantity, pricelists, currency
    ):
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

    def _get_best_applicable_pricelist_item(self, date, quantity, pricelists, currency):
        return self.env["product.pricelist.item"].browse(
            self._get_best_applicable_pricelist_item_id(
                date, quantity, pricelists, currency
            )
        )

    def _prepare_sellers(self, params=False):
        sellers = super()._prepare_sellers(params)
        # makes sure we process the list of sellers in the same order as the
        # one defined on the supplierinfo
        sellers = sellers.sorted(
            lambda a: (a.is_null_date_start, a.date_start, -a.min_qty, -a.min_qty_sale)
        )
        # filter out the ones that are not applicable for the current quantity based on the min_qty_sale
        return self._filter_for_min_sale_qty(sellers)

    def _filter_for_min_sale_qty(self, sellers):
        quantity = self.env.context.get("quantity")
        uom_id = self.env.context.get("uom_id")
        if not quantity:
            return sellers
        selected_ids = []
        for seller in sellers:
            quantity_uom_seller = quantity
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(
                    quantity_uom_seller, seller.product_uom
                )
            if quantity_uom_seller < seller.min_qty_sale:
                continue
            selected_ids.append(seller.id)
        return self.seller_ids.browse(selected_ids)

    def _select_seller(
        self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False
    ):
        self_with_context = self.with_context(
            quantity=quantity, date=date, uom_id=uom_id
        )
        return super(ProductProduct, self_with_context)._select_seller(
            partner_id=partner_id,
            quantity=quantity,
            date=date,
            uom_id=uom_id,
            params=params,
        )
