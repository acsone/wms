# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase App",
    "description": """
        Gather all purchase related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "purchase",
        "purchase_delivery_split_date",
        "purchase_stock_packaging",
        "purchase_cancel_reason",
        "alc_additional_product_purchase",
        "alc_incoming_product_supplier_filter",
        "alc_purchase_announced_delivery_date",
        "alc_purchase_order_cleaner",
        "alc_purchase_prepaid",
        "alc_stock_move_list",
        "alc_supplier_purchase_manager",
        "alc_supplier_purchase_manager_account",
        "alc_product_supplier",
        "alc_product_supplierinfo_force_edit_form",
        "alc_product_state",
        "alc_product_food",
        "alc_product_additional_price",
        "alc_product_price_import",
        "alc_stock_lot_track_food",
        "alc_stock_receive_lot",
        "partner_manual_rank",
        "product_uom_updatable",
    ],
}
