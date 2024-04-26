# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Available Product Expiry",
    "description": """
        Exclude expired lot from qty_available""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "depends": [
        "stock",
        "stock_available_immediately_exclude_location",  # to avoid a glue module
        "stock_available_location_get_domain",  # to avoid a glue module
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "installable": True,
}
