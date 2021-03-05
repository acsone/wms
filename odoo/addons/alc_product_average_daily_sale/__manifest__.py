# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Average Daily Sale",
    "description": """
        Alcyon: Compute the average daily sales of products

        The computation of the average daily sales depends of the ABC
        classification of the product. The analyzed sale period and a factor
        used to exclude sales out of the computed standard deviation are
        specified by classification level.

        The computation is done by a materialized view refreshed daily
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "sale",
        "alc_product_abc_classification",
        "alc_product_mto",
        "alc_product_picking_zone",
    ],
    "data": [
        "security/alc_product_average_daily_sale_config.xml",
        "views/alc_product_average_daily_sale_config.xml",
        "security/alc_average_daily_sale.xml",
        "views/alc_average_daily_sale.xml",
        "data/alc_product_average_daily_sale_config.xml",
        "data/ir_cron.xml",
    ],
}
