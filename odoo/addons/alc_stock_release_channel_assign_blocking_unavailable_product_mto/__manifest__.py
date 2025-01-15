# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Assign Blocking Unavailable Product Mto",
    "summary": """This module allows to exclude MTO generated moves for release channel assignation blocking""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "product_route_mto",
        "stock_route_mto",
        # Alcyon
        "alc_stock_release_channel_assign_blocking_unavailable_product",
    ],
}
