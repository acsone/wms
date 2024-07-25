# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields

from odoo.addons.stock.models.product import Product


class ProductProduct(Product):

    is_missing_default_orderpoint_for_mto = fields.Boolean(
        compute="_compute_is_missing_default_orderpoint_for_mto",
    )

    @api.depends("is_mto", "orderpoint_ids", "type")
    def _compute_is_missing_default_orderpoint_for_mto(self):
        for product in self:
            product.is_missing_default_orderpoint_for_mto = (
                product.is_mto
                and product.type == "product"
                and not product.with_context(active_test=False).orderpoint_ids
            )

    def _create_default_orderpoint_for_mto(self):
        default_company = self.env["res.company"]._get_main_company()
        for company, products in self.partition("company_id").items():
            company = company or default_company
            warehouses = self.env["stock.warehouse"].search(
                [("company_id", "=", company.id)]
            )
            for product in products:
                if not product.is_missing_default_orderpoint_for_mto:
                    continue
                for warehouse in warehouses:
                    vals = product._prepare_missing_orderpoint_vals(warehouse)
                    self.env["stock.warehouse.orderpoint"].create(vals)

    def _prepare_missing_orderpoint_vals(self, warehouse):
        self.ensure_one()
        return {
            "warehouse_id": warehouse.id,
            "product_id": self.id,
            "company_id": warehouse.company_id.id,
            "product_min_qty": 0,
            "product_max_qty": 0,
            "location_id": warehouse.view_location_id.id,
            "product_uom": self.uom_id.id,
        }

    def _ensure_default_orderpoint_for_mto(self):
        """Ensure that a default orderpoint is created for the MTO products.

        that have no orderpoint yet.
        """
        self.filtered(
            "is_missing_default_orderpoint_for_mto"
        )._create_default_orderpoint_for_mto()

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        products.sudo()._ensure_default_orderpoint_for_mto()
        return products

    def write(self, vals):
        res = super().write(vals)
        self.sudo()._ensure_default_orderpoint_for_mto()
        return res
