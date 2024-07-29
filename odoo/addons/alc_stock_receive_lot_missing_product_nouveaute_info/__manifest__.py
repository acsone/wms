# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Lot Missing Product Nouveaute Info",
    "description": """
        Force to enter product infos (weight, volume, ...) at the first reception of a product""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_barcode_required",
        "alc_product_category_data",
        "alc_product_dimensions_missing",
        "alc_product_pharmacy",
        "alc_stock_receive_lot",
        # OCA
        "product_route_mto",
        # fmt: on
    ],
    "data": [
        "security/res_groups.xml",
        "security/alc_new_product_reception.xml",
        "views/res_config_settings_views.xml",
        "views/stock_picking.xml",
        "wizards/stock_pack_operation_lot_add.xml",
    ],
    "demo": [],
    "installable": True,
}
