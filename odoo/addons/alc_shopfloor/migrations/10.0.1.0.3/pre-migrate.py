# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    food_profile = env["shopfloor.profile"].search([("name", "=", "Aliments")])
    if food_profile:
        xml_reference = env.ref(
            "alc_shopfloor.shopfloor_profile_ali", raise_if_not_found=False
        )
        if xml_reference:
            xml_reference.unlink()
        vals_data = {
            "module": "alc_shopfloor",
            "name": "shopfloor_profile_ali",
            "model": "shopfloor.profile",
            "res_id": food_profile.id,
        }
        env["ir.model.data"].create(vals_data)
