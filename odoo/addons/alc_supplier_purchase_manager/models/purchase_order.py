# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base.models.res_users import Users
from odoo.addons.purchase.models.purchase import PurchaseOrder as PurchaseOrderBase


class PurchaseOrder(PurchaseOrderBase):

    user_id = fields.Many2one[Users](
        compute="_compute_user_id", store=True, readonly=False, default=None
    )
    purchase_manager_id = fields.Many2one[Users](
        string="Purchase Manager",
        compute="_compute_purchase_manager_id",
        store=True,
        index=True,
    )

    @api.depends("partner_id")
    def _compute_purchase_manager_id(self):
        for purchase in self:
            purchase.purchase_manager_id = purchase.partner_id.purchase_manager_id

    @api.depends("partner_id")
    def _compute_user_id(self):
        for rec in self:
            rec.user_id = (
                rec.partner_id.purchase_manager_id
                if rec.partner_id.purchase_manager_id
                else self.env.user
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("partner_id") and not vals.get("user_id", True):
                vals.pop("user_id")
        return super().create(vals_list)
