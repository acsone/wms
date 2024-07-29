# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking exclude apply dynamic routing",
    "description": """ignore dynamic routing in cluster picking scenario when
    validation the batch""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "shopfloor",
        "stock_dynamic_routing",
        # fmt: on
    ],
}
