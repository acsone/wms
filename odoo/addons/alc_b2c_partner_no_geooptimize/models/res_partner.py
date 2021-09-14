# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _inverse_is_b2c_customer(self):
        res = super(ResPartner, self)._inverse_is_b2c_customer()
        self.filtered("is_b2c_customer").write({"not_in_dynamic_delivery_round": True})
        return res

    @api.onchange("is_b2c_customer")
    def _onchange_is_b2c_customer(self):
        for record in self.filtered("is_b2c_customer"):
            record.not_in_dynamic_delivery_round = True

    @api.multi
    def _write(self, vals):
        if vals.get("is_b2c_customer"):
            vals["not_in_dynamic_delivery_round"] = True
        return super(ResPartner, self)._write(vals)
