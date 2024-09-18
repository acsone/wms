# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Rma Shipment Advice",
    "description": """Alc Rma Shipment Advice""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "rma_sale",
        "shipment_advice",
        "shipment_advice_planner_toursolver",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/shipment_advice.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": [],
}
