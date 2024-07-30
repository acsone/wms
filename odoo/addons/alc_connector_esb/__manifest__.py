# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Specific legacy controllers used by Newpharam and Olalux?",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Connector",
    "depends": [
        # Custom
        "alc_pricelist_discount",
        "alc_product_cnk",
        "alc_product_sku",
        "alc_queue_job_background_channel",
        "alc_sale_auto_confirm_max_delay",
        "alc_sale_channel",
        "alc_sale_delay",
        "alc_sale_exception",
        "alc_sale_product_qty_unavailable",
        "alc_sale_suite_name",
        "alc_supplier_promotion",
        # OCA
        "onchange_helper",
        "queue_job",
        "stock_available",
        # Others
        "delivery",
        "web",
    ],
    "data": [
        "data/sale_channel.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "views/sale_order.xml",
        "views/delivery_carrier.xml",
    ],
    "installable": True,
}
