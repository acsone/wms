# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AlcClassified(models.Model):

    _name = "alc.classified"
    _inherit = ["mixin.user_id", "alc.classified"]

    def _get_default_user_id(self):
        res = super(AlcClassified, self)._get_default_user_id()
        user = self.env.ref("__setup__.res_user_jmercy", raise_if_not_found=False)
        return user or res

    def submit(self):
        res = super(AlcClassified, self).submit()
        template_xmlid = "alc_eshop_classifieds_responsible.submit_mail_template"
        self.notify_responsible(template_xmlid)
        return res
