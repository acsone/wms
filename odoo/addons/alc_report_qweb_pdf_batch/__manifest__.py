# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report QWeb PDF Batch",
    "summary": """
        Split pdf conversion in small batches to avoid memory issues""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Others
        "base",
        "base_setup",
        # fmt: on
    ],
    "data": ["data/ir_config_parameter.xml", "views/res_config_settings_views.xml"],
    "demo": [],
    "installable": True,
}
