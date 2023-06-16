# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_release_channel_geoengine.models.res_partner import (
    ResPartner as Partner,
)


class ResPartner(Partner):

    no_release_channel = fields.Boolean(
        default=False,
        compute="_compute_no_release_channel",
        store=True,
        index=True,
    )

    no_pharmacist = fields.Boolean(
        default=False,
        compute="_compute_no_pharmacist",
        store=True,
        index=True,
    )
    has_anomaly = fields.Boolean(
        default=False, compute="_compute_has_anomaly", store=True, index=True
    )

    @api.depends("active", "is_customer", "stock_release_channel_ids")
    def _compute_no_release_channel(self):
        alcyon_delivery_id = self.env.ref(
            "__setup__.deliver_carrier_alcyon", raise_if_not_found=False
        )
        for partner in self:
            if (
                partner.is_customer
                and partner.active
                and alcyon_delivery_id
                and partner.property_delivery_carrier_id.id == alcyon_delivery_id.id
                and not partner.stock_release_channel_ids
                and not partner.located_in_stock_release_channel_ids
            ):
                partner.no_release_channel = True
            else:
                partner.no_release_channel = False

    @api.depends("active", "is_customer", "partner_type", "pharmacist_id")
    def _compute_no_pharmacist(self):
        for partner in self:
            if (
                partner.is_customer
                and partner.active
                and partner.partner_type == "veterinary"
                and not partner.pharmacist_id
            ):
                partner.no_pharmacist = True
            else:
                partner.no_pharmacist = False

    @api.depends("no_release_channel", "no_pharmacist")
    def _compute_has_anomaly(self):
        for partner in self:
            if partner.no_release_channel or partner.no_pharmacist:
                partner.has_anomaly = True
            else:
                partner.has_anomaly = False
