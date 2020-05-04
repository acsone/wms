# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Specific product for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": ["product_price_category", "sale", "stock", "specific_data"],
    "website": "https://www.camptocamp.com",
    "data": [
        "data/product_price_category.xml",
        "data/product_storage_temperature.xml",
        "views/product_pricelist.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
