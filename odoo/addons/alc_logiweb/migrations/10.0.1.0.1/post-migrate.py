# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    existing_logiweb_partner = env["res.partner"].search([("ref", "=", "103115")])
    if existing_logiweb_partner:
        env.ref("alc_logiweb.logiweb_partner").unlink()
        vals_data = {
            "module": "alc_logiweb",
            "name": "logiweb_partner",
            "model": "res.partner",
            "res_id": existing_logiweb_partner.id,
        }
        env["ir.model.data"].create(vals_data)
