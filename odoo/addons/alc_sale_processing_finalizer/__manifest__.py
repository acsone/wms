# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Processing Finalizer",
    "description": """
        Allow to automatically close a Sale after a given period of time. """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "base",
        "delivery",
        "queue_job_cron",
        "sale",
        "sale_cancel_remaining",
        "specific_sale",
    ],
    "data": [
        "views/sale_order.xml",
        "data/ir_cron.xml",
        "data/mail_template_30.xml",
        "data/delivery_carrier_long_term.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
