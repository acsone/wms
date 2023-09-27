# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import api
from odoo.tools import float_compare

from odoo.addons.stock.models.stock_orderpoint import (
    StockWarehouseOrderpoint as StockWarehouseOrderpointBase,
)

_logger = logging.getLogger(__name__)

MANAGE_DAY_PREFIX = "is_manage_day_"


class StockWarehouseOrderpoint(StockWarehouseOrderpointBase):
    def _procure_orderpoint_confirm(
        self, use_new_cursor=False, company_id=None, raise_user_error=True
    ):
        """Run the procurement and recompute promotions if not disabled."""

        # if we are running from the resupply wizard, first make sure all
        # products with a negative stock have a procurement order
        if not company_id:
            company_id = self.env.company
        warehouses = self.env["stock.warehouse"].search(
            [("company_id", "=", company_id.id)]
        )
        missing_orderpoint_ids = set()
        for warehouse in warehouses:
            missing_orderpoint_ids.update(
                self._create_missing_orderpoint(warehouse).ids
            )
        missing_orderpoint_ids.update(self._filter_orderpoint_to_process().ids)
        to_process = self.env["stock.warehouse.orderpoint"].browse(
            missing_orderpoint_ids
        )
        _logger.info("Run the procurement")
        result = super(
            StockWarehouseOrderpoint, to_process
        )._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor,
            company_id=company_id,
            raise_user_error=raise_user_error,
        )
        _logger.info("Procurement finished")

        return result

    def _filter_orderpoint_to_process(self):
        return self.filtered_domain(self._filter_orderpoint_to_process_domain())

    @api.model
    def _create_missing_orderpoint(self, warehouse, products=None):
        product_model = self.env["product.product"].with_context(warehouse=warehouse.id)
        products = product_model.search(self._get_missing_orderpoint_domain(products))
        vals_list = self._prepare_missing_orderpoint_list_vals(warehouse, products)
        if vals_list:
            return self.create(vals_list)
        return self.browse()

    @api.model
    def _get_missing_orderpoint_domain(self, products=None):
        domain = [("orderpoint_ids", "=", False), ("type", "=", "product")]
        if products:
            domain.append(("id", "in", products.ids))
        return domain

    @api.model
    def _prepare_missing_orderpoint_list_vals(self, warehouse, products):
        list_vals = []
        precision_name = (
            self.env["product.product"]._fields["virtual_available"]._digits
        )
        decimal_precision = self.env["decimal.precision"].search(
            [("name", "=", precision_name)], limit=1
        )
        for product in products:
            if (
                float_compare(
                    product.virtual_available,
                    0,
                    precision_digits=decimal_precision.digits,
                )
                < 0
            ):
                list_vals.append(
                    self._prepare_missing_orderpoint_vals(warehouse, product)
                )
        return list_vals

    @api.model
    def _prepare_missing_orderpoint_vals(self, warehouse, product):
        return {
            "warehouse_id": warehouse.id,
            "product_id": product.id,
            "company_id": warehouse.company_id.id,
            "product_min_qty": 0,
            "product_max_qty": 0,
            "location_id": warehouse.lot_stock_id.id,
            "product_uom": product.uom_id.id,
        }

    def _filter_orderpoint_to_process_domain(self):
        domain = []
        if self._context.get("procure_type") == "by_suppliers":
            domain = [("product_id.supplier_id", "in", self._context["supplier_ids"])]
        elif self._context.get("procure_type") == "by_days":
            days_selected = []
            for key in self._context.keys():
                if key.startswith(MANAGE_DAY_PREFIX):
                    days_selected.append(key)

            # If there are selected days we build a new domain
            if days_selected:
                day = days_selected.pop()
                domain = [(f"product_id.supplier_id.{day}", "=", True)]
                while days_selected:
                    day = days_selected.pop()
                    # Insert the OR operator
                    domain.insert(0, "|")
                    domain.append((f"product_id.supplier_id.{day}", "=", True))
        else:
            isoweekday = datetime.now().isoweekday()
            field_name = MANAGE_DAY_PREFIX + str(isoweekday)
            domain = [(f"product_id.supplier_id.{field_name}", "=", True)]

            # Add suppliers with open purchase order in the
            open_purchase_orders = self.env["purchase.order"].search(
                [("state", "=", "draft")]
            )
            partners = open_purchase_orders.partner_id
            if partners:
                domain.insert(0, "|")
                domain.append(("product_id.supplier_id.id", "in", partners.ids))
        return domain
