# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Lot Missing Product Nouveaute Info",
    "description": """
        Force to enter product infos (weight, volume, ...) at the first reception of a product""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "alc_product_is_new",
        "alc_product_barcode_required",
        "alc_product_audit",
        "stock_receive_lot",
        "alc_product_pharmacy",
        "alc_product_mto",
    ],
    "data": [
        "security/res_groups.xml",
        "security/alc_new_product_reception.xml",
        "views/stock_picking.xml",
        "wizards/stock_pack_operation_lot_add.xml",
    ],
    "demo": [],
}
