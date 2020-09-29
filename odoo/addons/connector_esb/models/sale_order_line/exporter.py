# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from ...components.mapper import falsy2zero


class SaleOrderLineExportChildMapper(Component):
    _name = "esb.sale.order.line.export.child.mapper"
    _inherit = ["base.map.child.export"]
    _apply_on = "sale.order.line"

    def skip_item(self, record):
        """Do not export lines that contains delivery information."""
        return "is_delivery" in record.source and record.source.is_delivery


class SaleOrderLineExportMapper(Component):
    _name = "esb.sale.order.line.export.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "sale.order.line"

    direct = [
        (falsy2zero("product_uom_qty"), "qty_ordered"),
        (falsy2zero("qty_delivered"), "qty_delivered"),
        (falsy2zero("price_reduce_taxexcl"), "price"),
        (falsy2zero("price_reduce_taxinc"), "price_inc_tax"),
        (falsy2zero("product_qty_canceled"), "qty_cancelled"),
        (falsy2zero("product_qty_backorder"), "qty_backorder"),
    ]

    @mapping
    def compute_line_number(self, record):
        """The identifiant of the line.

        Following changes in specs, when creating a sale order
        send Odoo id; when doing an update send the esb_ref.
        The esb_ref is set to the magento line ID after creation of
        the sales order on Magento.
        """
        if self.options.for_create:
            line_number = record.id
        else:
            line_number = record.esb_ref
        return {"line_number": line_number}

    @mapping
    def compute_sku(self, record):
        return {"sku": record.product_id.default_code or ""}
