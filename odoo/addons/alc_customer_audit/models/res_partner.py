# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    no_delivery_round = fields.Boolean(
        default=False, compute="_compute_no_delivery_round", store=True, index=True,
    )

    no_pharmacist = fields.Boolean(
        default=False, compute="_compute_no_pharmacist", store=True, index=True,
    )
    has_anomaly = fields.Boolean(
        default=False, compute="_compute_has_anomaly", store=True, index=True
    )

    @api.depends("active", "customer", "round_itinerary_ids")
    def _compute_no_delivery_round(self):
        alcyon_delivery_id = self.env.ref(
            "__setup__.deliver_carrier_alcyon", raise_if_not_found=False
        )
        for partner in self:
            if (
                partner.customer
                and partner.active
                and alcyon_delivery_id
                and partner.property_delivery_carrier_id.id == alcyon_delivery_id.id
                and not partner.round_itinerary_ids
            ):
                partner.no_delivery_round = True
            else:
                partner.no_delivery_round = False

    @api.depends("active", "customer", "alcyon_category_id", "pharmacist_id")
    def _compute_no_pharmacist(self):
        veterinary = self.env.ref("specific_partner.partner_category_veterinary")
        for partner in self:
            if (
                partner.customer
                and partner.active
                and partner.alcyon_category_id.id == veterinary.id
                and not partner.pharmacist_id
            ):
                partner.no_pharmacist = True
            else:
                partner.no_pharmacist = False

    @api.depends("no_delivery_round", "no_pharmacist")
    def _compute_has_anomaly(self):
        for partner in self:
            if partner.no_delivery_round or partner.no_pharmacist:
                partner.has_anomaly = True
            else:
                partner.has_anomaly = False
