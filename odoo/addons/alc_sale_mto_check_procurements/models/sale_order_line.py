# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):
    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        res = super()._action_launch_stock_rule(previous_product_uom_qty)
        self._check_procurements_for_MTO_products()
        return res

    def _check_procurements_for_MTO_products(self):
        # ALCYN-2150: when a product with the MTO route is sold, we want to
        # check for reordering rules and generate a purchase immediately if
        # some stock is missing. The MTO route is an empty shell and is used
        # simply as a flag on the products, because it is important that the
        # resupply for the products are not chained to the deliveries -> use
        # orderpoint to trigger a MTS resupply actually.
        if not self:
            return
        route_mto = self.env.ref("stock.route_warehouse0_mto")
        lines = self.filtered(lambda r: r.state == "sale")
        products = lines.mapped("product_id").filtered(
            lambda rec: route_mto in rec.route_ids
        )
        if not products:
            # short cut, and especially don't call ensure_product_orderpoints
            # with an empty recordset, as this will ensure orderpoints for
            # *all* products
            return
        warehouse = lines.mapped("order_id.warehouse_id")
        orderpoints = self.env["stock.warehouse.orderpoint"].search(
            [
                ("product_id", "in", products.ids),
                ("warehouse_id", "=", warehouse.id),
                ("location_id", "child_of", warehouse.view_location_id.id),
            ]
        )
        if orderpoints:
            orderpoints._procure_orderpoint_confirm(
                company_id=self.mapped("order_id.company_id")
            )
