# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class ResPartnerCategory(models.Model):
    _inherit = "res.partner.category"

    def unlink(self):
        delivery_person_category = self.env.ref(
            "alc_partner_delivery_person.res_partner_category_delivery_person"
        )
        if delivery_person_category in self:
            raise UserError(_("The category 'Delivery person' can't be removed."))
        return super(ResPartnerCategory, self).unlink()
