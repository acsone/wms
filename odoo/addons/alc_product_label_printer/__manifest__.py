# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product label printer",
    "description": """
        Add a printer field on users to use when printing products label""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "base_report_to_printer",
        # fmt: on
    ],
    "data": ["views/res_users.xml"],
    "demo": [],
    "installable": True,
}
