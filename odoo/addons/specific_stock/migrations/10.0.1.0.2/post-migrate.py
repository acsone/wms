# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Add route on 'Product Souverain Frigo'")

    env = api.Environment(cr, SUPERUSER_ID, {})
    route = env.ref(
        "__setup__.stock_location_route_pick_froid", raise_if_not_found=False
    )
    product_template = env.ref("specific_stock.product_colis_souverain_frigo")

    if route:
        product_template.write({"route_ids": [(6, 0, route.ids)]})
    return
