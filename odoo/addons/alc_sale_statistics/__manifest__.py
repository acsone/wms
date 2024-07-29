# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Statistics",
    "description": """
        Add a way to export a report showing sale stock moves for a specific customer""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_type",
        "alc_partner_veterinary",
        "alc_product_additional_price",
        "alc_product_supplier",
        "alc_sale_channel",
        # OCA
        "sale_channel",
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "views/res_partner.xml",
        "views/alc_stock_move_report.xml",
        "security/alc_sale_statistics_security.xml",
    ],
    "demo": [],
    "installable": True,
}
