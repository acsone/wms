# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product label printing",
    "summary": """
        Add code needed to print products labels""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_b2c_partner",
        "alc_label_printing_base",
        "alc_partner_veterinary",
        # OCA
        "stock_procurement_customer",
        # Others
        "product_expiry",
        # fmt: on
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_lot_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_move_views.xml",
        "wizards/print_label.xml",
    ],
    "demo": [],
    "installable": True,
}
