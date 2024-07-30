# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Location Orderpoint Cleanup",
    "description": """
        Allows to define crons to clean replenishments""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "queue_job_cron",
        "stock_location_orderpoint_average_daily_sale",
        "stock_location_orderpoint_cleanup",
    ],
    "data": [
        "data/res_users.xml",
        "data/ir_cron.xml",
    ],
}
