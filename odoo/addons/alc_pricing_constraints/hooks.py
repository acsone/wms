# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import odoo

_logger = logging.getLogger()


def pre_init_hook(cr):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    domain_useless = [
        "|",
        "&",
        ("compute_price", "=", "percentage"),
        ("percent_price", "=", 0),
        "&",
        ("compute_price", "=", "formula"),
        "&",
        ("price_discount", "=", 0),
        ("price_surcharge", "=", 0),
    ]
    items_useless = env["product.pricelist.item"].search(domain_useless)
    _logger.info("Delete %s useless items.", len(items_useless))
    items_useless.unlink()  # will trigger quite a lot of recomputes...
