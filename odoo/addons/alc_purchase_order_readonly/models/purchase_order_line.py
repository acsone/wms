# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.account.models.account_tax import AccountTax
from odoo.addons.purchase.models.purchase import (
    PurchaseOrderLine as PurchaseOrderLineBase,
)

from .purchase_order import READONLY_LAX_STATES, READONLY_STATES


class PurchaseOrderLine(PurchaseOrderLineBase):

    name = fields.Text(readonly=False, states=READONLY_STATES)
    date_planned = fields.Datetime(readonly=False, states=READONLY_LAX_STATES)
    product_qty = fields.Float(readonly=False, states=READONLY_STATES)
    taxes_id = fields.Many2many[AccountTax](readonly=False, states=READONLY_STATES)
    discount_global = fields.Float(readonly=False, states=READONLY_STATES)
    promotion_supplier = fields.Float(readonly=False, states=READONLY_STATES)
