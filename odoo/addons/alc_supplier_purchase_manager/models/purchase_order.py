# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base.models.res_users import Users
from odoo.addons.purchase.models.purchase import PurchaseOrder as PurchaseOrderBase


class PurchaseOrder(PurchaseOrderBase):

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
