# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

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
        if self._is_filter_on_orderpoint_scheduler_enabled():
            to_process = self._filter_orderpoint_to_process()
        else:
            to_process = self
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

    def _is_filter_on_orderpoint_scheduler_enabled(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_stock_scheduler_filter.apply_filter_on_orderpoint_scheduler"
            )
        )

    def _filter_orderpoint_to_process(self):
        return self.filtered_domain(self._filter_orderpoint_to_process_domain())

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
