# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Additional Product Purchase",
    "description": """
        This addon define additional product in sale flow""",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "category": "Product",
    "depends": [
        "sale",
        "alc_partner_pricelist",
        "alc_pricelist_discount",
        "alc_supplier_promotion",
    ],
    "data": [],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
