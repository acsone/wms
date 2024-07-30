# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Order Line Cancel Available To Promise Release",
    "description": """
        Allows to check if sale line cancel will not cancel a picking line""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "sale_order_line_cancel",
        "stock_available_to_promise_release",
    ],
}
