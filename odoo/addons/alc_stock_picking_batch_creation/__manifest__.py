# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Batch Creation",
    "description": """
        stock picking batch creation""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "stock_picking_batch_creation",
        # fmt: on
    ],
    "data": [
        "data/devices.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "installable": True,
}
