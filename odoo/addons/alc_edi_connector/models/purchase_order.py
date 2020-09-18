# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    is_edi_available = fields.Boolean(
        related="partner_id.use_edi_connector", readonly=True
    )
    can_send_ubl_document = fields.Boolean(compute="_compute_can_send_ubl_document")

    @api.depends("partner_id.use_edi_connector", "state")
    def _compute_can_send_ubl_document(self):
        is_purchase_order_manager = self.env.user.has_group(
            "alc_edi_connector.purchase_order_manager"
        )
        for rec in self:
            rec.can_send_ubl_document = (
                is_purchase_order_manager
                and rec.partner_id.use_edi_connector
                and rec.state == "approved"
            )

    def check_can_send_ubl_document(self):
        for rec in self:
            if not rec.can_send_ubl_document:
                rec.partner_id.check_is_edi_supported()
                if rec.state != "approved":
                    raise UserError(
                        _(
                            "Sending UBL Order document is only allowed in "
                            "state approved"
                        )
                    )
                else:
                    raise UserError(
                        _(
                            "Sending UBL Order document is not allowed in the current context."
                        )
                    )

    def send_ubl_order_document(self):
        for rec in self.suspend_security():
            rec.check_can_send_ubl_document()
            rec.partner_id.edi_backend_id.send_order_document(rec)
