# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    indexes = env["se.index"].search([])
    indexes.filtered(
        lambda l: l.model_id
        == env.ref("alc_eshop_info_banner.model_alc_eshop_info_banner")
    ).write({"custom_tech_name": "eshop_info_banner"})
    indexes.filtered(
        lambda l: l.model_id == env.ref("alc_eshop_ads.model_alc_eshop_ads")
    ).write({"custom_tech_name": "eshop_ads"})
    indexes.filtered(
        lambda l: l.model_id == env.ref("shopinvader.model_shopinvader_category")
    ).write({"custom_tech_name": "shopinvader_category"})
    indexes.filtered(
        lambda l: l.model_id == env.ref("shopinvader.model_shopinvader_variant")
    ).write({"custom_tech_name": "shopinvader_variant"})
