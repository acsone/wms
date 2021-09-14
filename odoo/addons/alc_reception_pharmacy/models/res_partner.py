# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_delivered_by_alcyon = fields.Boolean(compute="_compute_is_delivered_by_alcyon")

    partner_shipping_id = fields.Many2one(
        "res.partner", string="Delivery Address", compute="_compute_partner_shipping_id"
    )

    @api.depends("child_ids")
    @api.multi
    def _compute_partner_shipping_id(self):
        """
        Trigger the change of the shipping address if the customer is modified.
        """
        for rec in self:
            address = rec.address_get(["delivery", "invoice"])
            rec.partner_shipping_id = address["delivery"]

    @api.depends(lambda self: self._is_delivered_by_alcyon_depends())
    @api.multi
    def _compute_is_delivered_by_alcyon(self):
        for rec in self:
            rec.is_delivered_by_alcyon = (
                len(rec.partner_shipping_id.round_itinerary_ids) > 0
            )

    @api.model
    def _is_delivered_by_alcyon_depends(self):
        return [
            "child_ids",
            "partner_shipping_id",
            "partner_shipping_id.round_itinerary_ids",
        ]
