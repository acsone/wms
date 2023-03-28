# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Pick Allowed",
    "description": """
        This addon adds a flag to release channels to define if the picking preparation
         is allowed or not. it also allows the definition per picking type.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["stock_release_channel"],
    "data": ["views/stock_picking_type.xml"],
    "demo": [],
}
