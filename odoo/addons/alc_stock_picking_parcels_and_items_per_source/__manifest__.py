# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Parcels and Items Per Origin",
    "description": """
        Allows to retrieve the number of parcels and items per origin""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "base_partition",
        "delivery_package_type_number_parcels",
        "delivery_procurement_group_carrier",
        "stock_move_zone_location_source",
        "stock_picking_delivery_link",
        # Others
        "delivery",
        "stock",
    ],
}
