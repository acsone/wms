# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.alc_registration.models import alc_registration
from odoo.addons.mixin_user_id.models.mixin_user_id import MixinUserId


class AlcRegistration(alc_registration.AlcRegistration, MixinUserId):

    _name = "alc.registration"

    def _get_default_user_id(self):
        res = super()._get_default_user_id()
        user = self.env.ref("__setup__.res_user_jmercy", raise_if_not_found=False)
        return user or res

    @api.model_create_multi
    def create(self, vals_list):
        no_send_self = self.with_context(tracking_disable=True)
        res = super(AlcRegistration, no_send_self).create(vals_list)
        template_xmlid = "alc_registration_responsible.create_mail_template"
        res.notify_responsible(template_xmlid)
        return res
