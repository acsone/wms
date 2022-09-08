# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_delivery_person = fields.Boolean(
        compute="_compute_is_delivery_person",
        inverse="_inverse_is_delivery_person",
        store=True,
        index=True,
    )

    @api.depends("category_id")
    def _compute_is_delivery_person(self):
        delivery_person_category = self.env.ref(
            "alc_partner_delivery_person.res_partner_category_delivery_person",
            raise_if_not_found=False,
        )
        if not delivery_person_category:
            # odoo init stage...
            for rec in self:
                rec.is_delivery_person = False
            return
        for rec in self:
            rec.is_delivery_person = delivery_person_category in rec.category_id

    def _inverse_is_delivery_person(self):
        delivery_person_category_id = self.env.ref(
            "alc_partner_delivery_person.res_partner_category_delivery_person"
        ).id
        to_unset = self.filtered(lambda n: not n.is_delivery_person)
        to_unset.write({"category_id": [(3, delivery_person_category_id)]})
        to_set = self.filtered(lambda n: n.is_delivery_person)
        to_set.write({"category_id": [(4, delivery_person_category_id)]})
