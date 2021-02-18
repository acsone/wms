# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Specific datas for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Base",
    "depends": [
        "base",
        "account",
        "product",
        "stock",
        "delivery",
        # FIXME specific_data should be at the root
        # of the custom addons, specific_partner as
        # other specific* should be a leaf...
        "specific_partner",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        "data/account_tax_group.xml",
        "data/product.category.csv",
        "data/product.pricelist.csv",
    ],
    "installable": True,
}
