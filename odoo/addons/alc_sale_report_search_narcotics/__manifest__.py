# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Report Search Narcotics",
    "description": """
        Allow searching for product of category narcotics in the sales report""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_product_category_data",
        # Others
        "sale",
    ],
    "data": ["views/sale_report.xml"],
    "demo": [],
}
