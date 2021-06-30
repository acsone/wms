# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    existing_partner = env["res.partner"].search([("ref", "=", "103187")])
    if existing_partner:
        env.ref("alc_b2c_partner.b2c_customer").unlink()
        vals_data = {
            "module": "alc_b2c_partner",
            "name": "b2c_customer",
            "model": "res.partner",
            "res_id": existing_partner.id,
        }
        env["ir.model.data"].create(vals_data)
