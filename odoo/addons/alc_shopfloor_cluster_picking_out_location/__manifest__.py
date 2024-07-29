# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking Out Location",
    "description": """
        backoffice for unloading cluster picking med location by location in the out""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "shopfloor",
        "stock_release_channel_shipment_advice_deliver",
        # fmt: on
    ],
    "data": ["views/stock_location.xml", "views/shopfloor_menu.xml"],
    "demo": [],
}
