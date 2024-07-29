# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Security",
    "description": """
        This addon add a security group for shopfloor users""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_shopfloor_user",
        # OCA
        "shopfloor_base",
        # Others
        "stock",
        # fmt: on
    ],
    "data": ["security/groups.xml", "security/ir.model.access.csv"],
    "demo": [],
    "post_init_hook": "_post_init_hook",
}
