# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma_sale.models.sale import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    def _prepare_rma_wizard_line_vals(self, data):
        vals = super()._prepare_rma_wizard_line_vals(data)
        vals["allowed_quantity"] = vals["quantity"]
        vals["quantity"] = 0
        return vals
