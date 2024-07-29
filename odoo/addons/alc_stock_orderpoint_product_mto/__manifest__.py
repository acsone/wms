# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Product Route MTO",
    "description": """
        This addon add a default order point on MTO product""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "base_partition",
        "product_route_mto",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
