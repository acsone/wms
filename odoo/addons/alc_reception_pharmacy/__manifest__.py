# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Reception Pharmacy",
    "description": """
        Alcyon: Manage reception of product from the Souverain pharmacy""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    # TODO split delivery_rounds...
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_delivered_by_alcyon",
        "alc_product_category_data",
        "alc_queue_job_background_channel",
        # OCA
        "base_partition",
        "delivery_procurement_group_carrier",
        "queue_job",
        "stock_picking_group_by_partner_by_carrier",
        "stock_procurement_customer",
        "stock_restrict_lot",
        "web_notify",
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/product_product.xml",
        "data/queue_job_function.xml",
        "wizards/receive_pharmacy_products.xml",
        "views/reception_pharmacy_views.xml",
        "views/reception_pharmacy_line_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "installable": True,
}
