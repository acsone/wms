# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Label Printing Reception",
    "description": """
        add permission for reception user to change printer""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Third-party
        "base_report_to_printer",
        # Alcyon
        "alc_product_label_printer",
        "alc_product_label_printing",
        # Alcyon/Stock Management
        "alc_stock_receive_lot",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizards/select_printing_printer.xml",
        "wizards/stock_receive.xml",
    ],
    "installable": True,
}
