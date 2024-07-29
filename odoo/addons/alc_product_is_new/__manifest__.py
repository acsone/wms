# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Is New",
    "description": """
        Flag for new products in alc""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "stock_storage_type",
        # fmt: on
    ],
    "data": [
        "data/stock_package_type.xml",
        "views/product_template_views.xml",
        "views/stock_package_type_views.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
