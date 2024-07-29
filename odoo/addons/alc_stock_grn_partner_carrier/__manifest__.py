# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock GRN Partner Carrier",
    "description": """
        Use carrier tagged partner as carrier in stock grn""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_carrier",
        # OCA
        "stock_grn",
        # fmt: on
    ],
    "data": ["views/stock_grn_views.xml"],
    "installable": True,
}
