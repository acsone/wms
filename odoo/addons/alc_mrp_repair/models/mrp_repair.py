# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class Repair(models.Model):

    _inherit = "mrp.repair"

    @api.model
    def default_get(self, fields_list):
        defaults = super(Repair, self).default_get(fields_list)
        sav_location = self.env.ref(
            "alc_mrp_repair.sav_stock_location", raise_if_not_found=False
        )
        if sav_location:
            defaults["location_id"] = sav_location.id
            defaults["location_dest_id"] = sav_location.id
        return defaults

    def action_repair_cancel_draft(self):
        if self.filtered(lambda repair: repair.state == "under_repair"):
            raise UserError(
                _("Repair cannot be set to draft when it is already started.")
            )
        super(Repair, self).action_repair_cancel()
        return super(Repair, self).action_repair_cancel_draft()

    def action_send_quote_email(self):
        """
        Based on `action_quotation_send`
        """
        self.ensure_one()
        ir_model_data = self.env["ir.model.data"]
        try:
            template_id = ir_model_data.get_object_reference(
                "alc_mrp_repair", "email_template_repair_order"
            )[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                "mail", "email_compose_message_wizard_form"
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update(
            {
                "default_model": "mrp.repair",
                "default_res_id": self.ids[0],
                "default_use_template": bool(template_id),
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "mark_so_as_sent": True,
                "custom_layout": "alc_mrp_repair.mail_template_data_notification_email_mrp_repair",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }
