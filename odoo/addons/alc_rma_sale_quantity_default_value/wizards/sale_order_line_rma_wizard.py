# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.rma_sale.wizard.sale_order_rma_wizard import (
    SaleOrderLineRmaWizard as SaleOrderLineRmaWizardBase,
)


class SaleOrderLineRmaWizard(SaleOrderLineRmaWizardBase):
    allowed_quantity = fields.Float(digits="Product Unit of Measure", readonly=True)
