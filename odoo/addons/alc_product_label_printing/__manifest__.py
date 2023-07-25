# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product label printing",
    "summary": """
        Add code needed to print products labels""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "alc_b2c_partner",
        "alc_label_printing_base",
        "alc_partner_veterinary",
        "stock_procurement_customer",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_lot_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_move_views.xml",
    ],
    "demo": [],
    "installable": True,
}
