# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Processing Finalizer",
    "description": """
        Allow to automatically close a Sale older than 3 months. """,
    "version": "16.0.1.0.6",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "delivery",
        "sale",
        "queue_job_cron",
        "sale_order_line_cancel",
        "alc_sale_order_line_product_type",
        "alc_sale_product_qty_unavailable",
        "alc_sale_consignment",
        "alc_queue_job_background_channel",
    ],
    "data": [
        "views/sale_order_views.xml",
        "views/delivery_carrier_views.xml",
        "views/res_config_settings_views.xml",
        "data/ir_cron.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "data/mail_template_30.xml",
    ],
    "installable": True,
}
