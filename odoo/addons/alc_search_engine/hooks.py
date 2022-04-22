# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    shop_backend = env.ref("alc_eshop.backend")
    es_backend = env["se.backend"].search([("tech_name", "=", "elasticsearch_backend")])
    if es_backend and shop_backend.se_backend_id != es_backend:
        shop_backend.se_backend_id = es_backend
