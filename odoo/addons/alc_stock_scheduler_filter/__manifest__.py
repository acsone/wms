# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Scheduler Filter",
    "description": """
        This addon enhance stock scheduler by adding filters for stock orderpoint
        selection in stock scheduling process""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["purchase_stock", "alc_product_supplier"],
    "data": [
        "views/res_config_settings.xml",
        "views/res_partner.xml",
        "wizards/stock_scheduler_compute.xml",
    ],
    "demo": [],
}
