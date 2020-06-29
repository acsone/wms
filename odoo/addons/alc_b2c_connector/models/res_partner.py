# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_b2c_customer = fields.Boolean(
        compute="_compute_is_b2c_customer",
        inverse="_inverse_is_b2c_customer",
        store=True,
        index=True,
    )

    @api.depends("category_id")
    def _compute_is_b2c_customer(self):
        bc2_category = self.env.ref(
            "alc_b2c_connector.res_partner_category_b2c_customer",
            raise_if_not_found=False,
        )
        if not bc2_category:
            # odoo init stage...
            for rec in self:
                rec.is_b2c_customer = False
            return
        for rec in self:
            rec.is_b2c_customer = bc2_category in rec.category_id

    def _inverse_is_b2c_customer(self):
        bc2_category_id = self.env.ref(
            "alc_b2c_connector.res_partner_category_b2c_customer"
        ).id
        to_unset = self.filtered(lambda n: not n.is_b2c_customer)
        to_unset.write({"category_id": [(3, bc2_category_id)]})
        to_set = self.filtered(lambda n: n.is_b2c_customer)
        to_set.write({"category_id": [(4, bc2_category_id)]})
