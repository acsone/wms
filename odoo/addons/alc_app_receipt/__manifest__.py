# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Receipt App",
    "description": """
        Gather all receipt related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # fmt: off
        # Custom
        "alc_stock_grn_partner_carrier",
        "alc_stock_grn_time_delay",
        "alc_stock_reception_rank",
        # OCA
        "stock_picking_grn_mandatory",
        # fmt: on
    ],
}
