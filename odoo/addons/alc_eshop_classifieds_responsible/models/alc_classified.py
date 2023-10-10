# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.alc_eshop_classifieds.models.alc_classified import AlcClassified
from odoo.addons.mixin_user_id.models.mixin_user_id import MixinUserId


class Classified(AlcClassified, MixinUserId):
    _name = "alc.classified"

    def _get_default_user_id(self):
        res = super()._get_default_user_id()
        user = self.env.ref("__setup__.res_user_jmercy", raise_if_not_found=False)
        return user or res

    def submit(self):
        res = super().submit()
        template_xmlid = "alc_eshop_classifieds_responsible.submit_mail_template"
        self.notify_responsible(template_xmlid)
        return res
