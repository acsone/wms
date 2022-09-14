# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Promotion Mailing",
    "description": """
        Alcyon: Send mails to subcribers when a subscription on a produt read
        its end date""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop",
        "alc_product_promotion_subscription",
        "mail",
        "pricelist_discount",
        "queue_job_cron",
        "sale",
        "report",
    ],
    "data": [
        "data/ir_cron.xml",
        "wizards/sale_config_settings.xml",
        "reports/report_alc_product_promotion_mailing.xml",
    ],
    "demo": [],
    'installable': False
}