# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Pricelist 2 Menu",
    "description": """
        Add a menu to edit the "Sale Price 2" pricelist""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_pricelist_data",
        # Others
        "sale",
        # fmt: on
    ],
    "data": ["views/product.pricelist_item.xml"],
}
