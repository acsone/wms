# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MixinUserId(models.AbstractModel):
    _name = "mixin.user_id"
    _inherit = "mail.thread"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        help="The user in charge of managing this record.",
        default=lambda r: r._get_default_user_id(),
    )

    @api.model
    def _get_default_user_id(self):
        return self.env.user

    def notify_responsible(self, template_xmlid):
        mail_template_id = self.env.ref(template_xmlid).id
        for record in self:
            ctx = {
                "default_email_to": record.user_id.email,
                "default_partner_ids": [],
                "default_model": self._name,
                "default_res_id": record.id,
                "default_use_template": bool(mail_template_id),
                "default_template_id": mail_template_id,
                "default_composition_mode": "comment",
            }
            record.with_context(ctx).message_post_with_template(mail_template_id)
