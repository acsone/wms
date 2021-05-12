# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref("alc_clubvetshop.alc_b2c_clubvetshop_backend").auth_api_key_id = env.ref(
        "alc_clubvetshop.api_key_clubvetshop_rest_api"
    )
