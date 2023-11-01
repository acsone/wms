# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.alc_veterinary_group.models.veterinary_group import (
    VeterinaryGroup as VeterinaryGroupBase,
)


class VeterinaryGroup(VeterinaryGroupBase):
    @api.model_create_multi
    def create(self, vals_list):
        groups = super().create(vals_list)
        for group, vals in zip(groups, vals_list, strict=True):
            if "partner_ids" in vals:
                group.partner_ids.keycloak_user_ids.check_update_on_keycloak_backend(
                    {"veterinary_group_ids": None}
                )
        return groups

    def write(self, vals):
        existing_partner_ids = set(self.partner_ids.ids)
        res = super().write(vals)
        if "partner_ids" in vals:
            new_partner_ids = set(self.partner_ids.ids)
            diff_partner_ids = existing_partner_ids ^ new_partner_ids
            self.env["res.partner"].browse(
                list(diff_partner_ids)
            ).keycloak_user_ids.check_update_on_keycloak_backend(
                {"veterinary_group_ids": None}
            )
        return res
