# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report Shipment Advice",
    "summary": """
        Shipment advice reporting for Alcyon""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_report_base",
        "alc_rma_shipment_advice",
        "alc_stock_picking_parcels_and_items_per_source",
        # OCA
        "internal_stock_quant_package",
        "shipment_advice_planner_toursolver",
        "shipment_advice_planner_toursolver",
        "shopfloor",
        "stock_move_zone_location_source",
        "stock_package_type_category",
        "stock_release_channel_shipment_advice",
        "stock_release_channel_shipment_advice",
    ],
    "data": [
        "views/stock_location.xml",
        "views/res_config_settings.xml",
        "security/security.xml",
        "data/paperformat.xml",
        "views/report_shipment_advice.xml",
        "views/stock_package_type_category.xml",
    ],
}
