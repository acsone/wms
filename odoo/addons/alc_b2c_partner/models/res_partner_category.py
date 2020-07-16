# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class ResPartnerCategory(models.Model):
    _inherit = "res.partner.category"

    def unlink(self):
        bc2_category = self.env.ref("alc_b2c_partner.res_partner_category_b2c_customer")
        if bc2_category in self:
            raise UserError(_("B2C category can't be removed."))
        return super(ResPartnerCategory, self).unlink()
