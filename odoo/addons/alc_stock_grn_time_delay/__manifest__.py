# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Grn Time Delay",
    "summary": """
        Add information about outdated receipt based on the GRN date""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "stock_grn",
        # Others
        "stock",
        # fmt: on
    ],
    "data": ["views/res_config_settings_views.xml", "views/stock_picking_views.xml"],
    "external_dependencies": {"python": ["numpy"]},
    "demo": [],
    "installable": True,
}
