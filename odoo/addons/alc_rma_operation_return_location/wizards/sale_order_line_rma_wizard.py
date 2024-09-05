# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma_sale.wizard.sale_order_rma_wizard import (
    SaleOrderLineRmaWizard as SaleOrderLineRmaWizardBase,
)


class SaleOrderLineRmaWizard(SaleOrderLineRmaWizardBase):
    def _prepare_rma_values(self):
        self.ensure_one()
        vals = super()._prepare_rma_values()
        if self.operation_id.return_location_id:
            vals["location_id"] = self.operation_id.return_location_id.id
        return vals
