# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Putaway App",
    "description": """
        Allows to collect all modules for putaway application""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        "alc_product_dimensions",
        "alc_stock_scrap_responsible",
        "product_abc_classification_sale_stock",
        "product_dimension",
        "stock_dynamic_routing",
        "stock_location_product_restriction",
        "stock_move_auto_assign",
        "stock_picking_start",
        "stock_storage_type",
        "stock_picking_start",
        "stock_storage_type_putaway_abc_classification_sale_stock",
    ],
}
