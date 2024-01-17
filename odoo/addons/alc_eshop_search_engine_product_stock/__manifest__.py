# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Product Stock",
    "description": """
        Alcyon: Recompute stock state only on incoming and outgoing moves""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop_product_domain",
        "alc_stock_move_direction",
        "queue_job_cron",
        "shopinvader_search_engine_product_stock",
    ],
    "data": ["data/ir_cron.xml"],
    "development_status": "Alpha",
}
