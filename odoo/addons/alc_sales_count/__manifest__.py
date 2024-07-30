# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sales Count",
    "description": """
        Improve the performance while sorting SO and SO lines (sort by internal reference and not by name otherwise the ORM creates a subselect on the translations in many requests)""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "sale_order_line_cancel",
    ],
    "data": [],
    "demo": [],
}
