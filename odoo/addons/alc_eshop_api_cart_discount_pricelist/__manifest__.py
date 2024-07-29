# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Cart Price List Discount",
    "summary": """
        Manage price list discount on cart transaction""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_pricelist_discount",
        # OCA
        "shopinvader_api_cart",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
