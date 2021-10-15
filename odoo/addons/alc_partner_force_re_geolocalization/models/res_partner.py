# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    coordinates_should_be_checked = fields.Boolean(default=False)

    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        for partner in self:
            if partner.customer and not partner.is_b2c_customer:
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
                coordinates_are_modified = any(
                    key in vals for key in ["partner_latitude", "partner_longitude"]
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
