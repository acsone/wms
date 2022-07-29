# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AlcRegistration(models.Model):

    _name = "alc.registration"
    _inherit = ["mixin.user_id", "alc.registration"]

    def _get_default_user_id(self):
        res = super(AlcRegistration, self)._get_default_user_id()
        user = self.env.ref("__setup__.res_user_jmercy", raise_if_not_found=False)
        return user or res

    @api.model
    def create(self, vals):
        no_send_self = self.with_context(tracking_disable=True)
        res = super(AlcRegistration, no_send_self).create(vals)
        template_xmlid = "alc_registration_responsible.create_mail_template"
        res.notify_responsible(template_xmlid)
        return res
