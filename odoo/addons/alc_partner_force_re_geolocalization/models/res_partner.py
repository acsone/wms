# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as PartnerBase


class ResPartner(PartnerBase):

    coordinates_should_be_checked = fields.Boolean(default=False)

    def write(self, vals):
        result = super().write(vals)
        for partner in self:
            if partner.customer_rank and not partner.is_b2c_customer:
                address_is_modified = any(
                    key in vals
                    for key in [
                        "street",
                        "street2",
                        "city",
                        "zip",
                        "country_id",
                        "state_id",
                    ]
                )
                #  When changing the address the coordinates are set to 0, so we only
                #  consider coordinates to be modified if they are not both 0.
                coordinates_are_modified = bool(
                    [
                        val
                        for key, val in vals.items()
                        if key in ["partner_latitude", "partner_longitude"] and val
                    ]
                )
                if partner.coordinates_should_be_checked and coordinates_are_modified:
                    partner.coordinates_should_be_checked = False

                if (
                    not partner.coordinates_should_be_checked
                    and address_is_modified
                    and not coordinates_are_modified
                ):
                    partner.coordinates_should_be_checked = True

        return result
