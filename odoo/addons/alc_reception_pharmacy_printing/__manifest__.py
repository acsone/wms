# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Reception Pharmacy Printing",
    "description": """
        Alcyon: Manage printing of reception pharmacy""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_printing_base",
        "alc_reception_pharmacy",
        # Others
        "product_expiry",
        # fmt: on
    ],
    "data": [
        "security/select_pharmacy_printing_printer.xml",
        "views/pharmacy_lot_label_report.xml",
        "views/reception_pharmacy_line_views.xml",
        "views/res_users_views.xml",
        "wizards/select_pharmacy_printing_printer.xml",
    ],
    "demo": [],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
