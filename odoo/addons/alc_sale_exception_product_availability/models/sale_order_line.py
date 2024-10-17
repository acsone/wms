# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.alc_sale_exception.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    def validate_no_backorder(self):
        """Block backorder for customer that specifically do not want them."""
        if not self.product_qty_unavailable:
            return False
        if not self.product_uom_qty:
            return False
        return not self.order_id.partner_id.sale_reason_backorder_strategy == "create"

    def warning_provision_on_order(self):
        """Add a warning if the product is provisioned at ordering time."""
        routes = self.product_id.route_ids
        return self.env.ref("stock.route_warehouse0_mto").id in routes.ids

    def warning_supplier_break(self):
        """Add a warning for out of stock product at the supplier."""
        supplier_nostock = self.env.ref("alc_product_state.product_state_h")
        if self.product_id.product_state_id != supplier_nostock:
            return False
        product = self.product_id.with_context(date=self.order_id.date_order)
        if product.immediately_usable_qty >= self.product_uom_qty:
            # Although it is out of stock at the supplier, there is still
            # enough stock in Alcyon warehouse
            return False
        if not self.product_uom_qty:
            return False
        return True
