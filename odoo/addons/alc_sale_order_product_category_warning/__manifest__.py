# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Order Product Category Warning",
    "description": """
        Shows warnings on product categories on the sale order print""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_partner_pharmacist",
        "alc_product_category_data",
        "alc_product_category_warning_info",
        "alc_sale_product_qty_unavailable",
        # OCA
        "sale_triple_discount",
        # Others
        "sale",
    ],
    "data": ["reports/ir_actions_report_template.xml"],
}
