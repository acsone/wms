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
        # Odoo Community
        "delivery",
        # Third-party
        "internal_stock_quant_package",
        "shipment_advice",
        "stock_package_type_category",
        # Alcyon
        "alc_additional_product_stock",
        "alc_b2c_partner",
        "alc_partner_suite",
        "alc_partner_veterinary",
        "alc_report_base",
        "alc_rma_stock_delivery_slip",
        "alc_sale_suite_name",
        "alc_stock_move_serial_number",
        "alc_stock_picking_parcels_and_items_per_source",
        "alc_stock_release_channel_print_shipment_advice",
        # Alcyon/Stock
        "alc_stock_delivery_slip",
        # Alcyon/Stock Management
        "alc_sale_consignment",
    ],
    "data": [
        "views/rma_operation.xml",
        "views/stock_release_channel.xml",
        "views/base_contact_views.xml",
        "views/res_partner_views.xml",
        "views/report_deliveryslip.xml",
        "views/shipment_advice_views.xml",
        "views/stock_picking_type_views.xml",
        "views/stock_package_type_category.xml",
        "views/res_config_settings.xml",
    ],
    "demo": [],
    "installable": True,
}
