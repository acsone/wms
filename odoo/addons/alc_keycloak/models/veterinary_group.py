# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class VeterinaryGroup(models.Model):

    _inherit = "veterinary.group"

    @api.model
    def create(self, vals):
        group = super(VeterinaryGroup, self).create(vals)
        if "partner_ids" in vals:
            group.partner_ids.mapped(
                "keycloak_user_ids"
            ).check_update_on_keycloak_backend({"veterinary_group_ids": None})
        return group

    def write(self, vals):
        existing_partner_ids = set(self.mapped("partner_ids").ids)
        res = super(VeterinaryGroup, self).write(vals)
        if "partner_ids" in vals:
            new_partner_ids = set(self.mapped("partner_ids").ids)
            diff_partner_ids = existing_partner_ids ^ new_partner_ids
            self.env["res.partner"].browse(list(diff_partner_ids)).mapped(
                "keycloak_user_ids"
            ).check_update_on_keycloak_backend({"veterinary_group_ids": None})
        return res
