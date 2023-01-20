# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Putaway App",
    "description": """
        Gather all putaway related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        "alc_product_packaging",
        "alc_product_packaging_dimension",
        "alc_product_dimensions",
        "alc_stock_scrap_responsible",
        "product_abc_classification_sale_stock",
        "product_dimension",
        "product_packaging_level",
        "product_packaging_level_pallet",
        "product_route_mto",
        "stock_average_daily_sale",
        "stock_dynamic_routing",
        "stock_location_product_restriction",
        "stock_location_zone",
        "stock_move_auto_assign",
        "stock_picking_start",
        "stock_route_mto",
        "stock_storage_type",
        "stock_picking_start",
        "stock_storage_type_putaway_abc_classification_sale_stock",
    ],
}
