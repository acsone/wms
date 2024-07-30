# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Supplier Promotions",
    "description": """Alcyon Supplier Promotions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_partner_type",
        "alc_product_supplier",
        "mixin_past",
        # OCA
        "base_sparse_field_list_support",
        # Others
        "product",
    ],
    "application": False,
    "data": ["views/product_supplierinfo.xml"],
    "demo": [],
    "installable": True,
}
