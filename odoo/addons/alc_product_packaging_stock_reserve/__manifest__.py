# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# TO BE REPLACED WHEN MIGRATING BY SOMETHING LIKE
# https://github.com/OCA/stock-logistics-warehouse/tree/13.0/stock_reserve_rule

{
    "name": "Stock Unit",
    "version": "10.0.1.0.0",
    "author": "BCIM, ACSONE SA/NV",
    "category": "Stock Management",
    "depends": ["stock", "alc_product_packaging"],
    "data": [
        "data/product_packaging_type.xml",
        "views/product_packaging_type.xml",
        "views/stock_config_settings.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
}
