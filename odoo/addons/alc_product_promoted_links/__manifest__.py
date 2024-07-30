# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Promoted Product",
    "description": """Alcyon Promoted Product""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "base_sparse_field_list_support",
        "product_template_multi_link",
    ],
    "data": [
        "data/product_template_link_type.xml",
        "views/product_template.xml",
        "views/product_product.xml",
    ],
}
