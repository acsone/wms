# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc label printing base",
    "summary": """
        Code foundation needed to print labels and package labels
        """,
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_printing_base",
        "alc_stock_release_channel_code",
        # OCA
        "delivery_package_type_number_parcels",
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/print_label.xml",
        "views/res_partner_views.xml",
        "views/stock_picking_views.xml",
    ],
    "demo": [],
    "installable": True,
}
