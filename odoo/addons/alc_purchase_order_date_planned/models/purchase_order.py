# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.purchase.models.purchase import PurchaseOrder as PurchaseOrderBase

READONLY_STATES = {
    "purchase": [("readonly", True)],
    "done": [("readonly", True)],
    "cancel": [("readonly", True)],
}


class PurchaseOrder(PurchaseOrderBase):

    date_planned = fields.Datetime(
        inverse="_inverse_date_planned", readonly=False, states=READONLY_STATES
    )

    def _inverse_date_planned(self):
        for rec in self:
            rec.order_line.update({"date_planned": rec.date_planned})
