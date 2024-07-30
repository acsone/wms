# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Packaging",
    "description": """
        Alcyon: Product packaging""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_product_template_packaging_search",
        # OCA
        "product_packaging_level",
        "product_packaging_level_pallet",
        "stock_storage_type",
    ],
    "data": [
        "data/product_packaging_type.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/product_packaging_views.xml",
    ],
    "installable": True,
}
