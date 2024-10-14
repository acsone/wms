# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_supplierinfo import SupplierInfo


class ProductSupplierInfo(SupplierInfo):
    delay = fields.Integer(
        compute="_compute_delay",
        default=None,
        readonly=False,
        store=True,
        precompute=True,
    )

    @api.depends("partner_id")
    def _compute_delay(self):
        for rec in self:
            if rec.partner_id.delivery_lead_time:
                rec.delay = rec.partner_id.delivery_lead_time
