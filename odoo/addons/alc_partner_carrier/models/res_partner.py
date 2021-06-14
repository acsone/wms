# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_carrier = fields.Boolean(
        compute="_compute_is_carrier",
        inverse="_inverse_is_carrier",
        store=True,
        index=True,
    )

    @api.depends("category_id")
    def _compute_is_carrier(self):
        carrier_category = self.env.ref(
            "alc_partner_carrier.res_partner_category_carrier",
            raise_if_not_found=False,
        )
        if not carrier_category:
            # odoo init stage...
            for rec in self:
                rec.is_carrier = False
            return
        for rec in self:
            rec.is_carrier = carrier_category in rec.category_id

    def _inverse_is_carrier(self):
        carrier_category_id = self.env.ref(
            "alc_partner_carrier.res_partner_category_carrier"
        ).id
        to_unset = self.filtered(lambda n: not n.is_carrier)
        to_unset.write({"category_id": [(3, carrier_category_id)]})
        to_set = self.filtered(lambda n: n.is_carrier)
        to_set.write({"category_id": [(4, carrier_category_id)]})
