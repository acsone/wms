# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc App Analytic",
    "description": """
        Allows to gather all modules for analytic flows""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "account_move_line_single_analytic_account",
        "alc_analytic_category_report",
        # OCA
        "account_analytic_account_tag",
        "account_analytic_required",
        "account_analytic_tag",
        "product_analytic",
        "product_analytic_purchase",
        "product_analytic_sale",
        # Others
        "analytic",
        # fmt: on
    ],
}
