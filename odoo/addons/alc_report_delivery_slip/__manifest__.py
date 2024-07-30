# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report Delivery Slip",
    "summary": """
        Delivery Slip reporting for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_b2c_partner",
        "alc_partner_suite",
        "alc_partner_veterinary",
        "alc_report_base",
        "alc_sale_consignment",
        "alc_sale_suite_name",
        "alc_stock_delivery_slip",
        "alc_stock_move_serial_number",
        "alc_stock_picking_parcels_and_items_per_source",
        "alc_stock_release_channel_print_shipment_advice",
        # OCA
        "shipment_advice",
        # Others
        "delivery",
    ],
    "data": [
        "views/stock_release_channel.xml",
        "views/base_contact_views.xml",
        "views/res_partner_views.xml",
        "views/report_deliveryslip.xml",
        "views/shipment_advice_views.xml",
        "views/stock_picking_type_views.xml",
    ],
    "demo": [],
    "installable": True,
}
