# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Qty Returned",
    "description": """
        This addon track qty returned in sale orders""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "sale_order_line_cancel",
    ],
    "data": ["views/sale_order.xml", "views/sale_order_line.xml"],
    "pre_init_hook": "pre_init_hook",
}
