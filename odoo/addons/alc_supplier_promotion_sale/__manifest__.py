# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Supplier Promotion Sale",
    "description": """
        This addon define additional product in sale flow""",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "category": "Product",
    "version": "16.0.1.0.0",
    "depends": [
        # Odoo Community
        "sale",
        # Alcyon
        "alc_partner_pricelist",
        "alc_supplier_promotion",
        # Alcyon/Sales Management
        "alc_pricelist_discount",
    ],
    "data": [],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
