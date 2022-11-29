# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    domain = [
        ("applied_on", "=", "1_product"),
        ("has_min_quantity", "=", True),
        ("is_past", "=", False),
    ]
    min_qty_items = env["product.pricelist.item"].search(domain)
    items_by_pricelists = min_qty_items.partition("pricelist_id")
    for pricelist, items in items_by_pricelists.items():
        pids = items.mapped("product_tmpl_id").ids
        domain_extend = [("product_tmpl_id", "in", pids)]
        pricelist.delay_update_price_cache(domain_extend=domain_extend)
