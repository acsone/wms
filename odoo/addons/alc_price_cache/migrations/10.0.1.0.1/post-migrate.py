# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Delay recompute price cache")
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    products = env["product.product"].search([])
    for batch in products.batch(100):
        batch.delay_update_price_cache()
