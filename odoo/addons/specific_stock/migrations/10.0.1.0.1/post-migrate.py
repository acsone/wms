# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Add route on 'Product Souverain Frigo'")

    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    route = env.ref("__setup__.picking_zone_frigo")
    product_template = env.ref("specific_stock.product_colis_souverain_frigo")

    if route:
        product_template.write({"route_ids": (4, route.id, False)})
    return
