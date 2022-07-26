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
    if items_useless:
        # deleting many items would create too many jobs;
        # at this point just recompute the cache for all products
        q = "DELETE FROM product_pricelist_item WHERE id in %s;"
        cr.execute(q, (tuple(items_useless.ids),))
        products = env["product.product"].search([])
        for product in products:
            product.delay_update_price_cache()
