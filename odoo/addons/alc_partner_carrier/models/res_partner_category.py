# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class ResPartnerCategory(models.Model):
    _inherit = "res.partner.category"

    def unlink(self):
        carrier_category = self.env.ref(
            "alc_partner_carrier.res_partner_category_carrier"
        )
        if carrier_category in self:
            raise UserError(_("The category 'Carrier' can't be removed."))
        return super(ResPartnerCategory, self).unlink()
