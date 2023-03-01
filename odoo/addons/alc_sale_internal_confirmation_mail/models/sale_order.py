# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        send_confirmation_email_internal = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_mail_internal.send_email", "False")
        )
        if send_confirmation_email_internal:
            for rec in self:
                if rec.sale_channel_id.is_internal:
                    rec._send_order_confirmation_mail()
        return res
