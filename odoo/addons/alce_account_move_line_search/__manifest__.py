# Copyright 2024 ACSONE SA/NV

{
    "name": "Account Move Line Search",
    "version": "16.0.1.0.0",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Odoo Enterprise
        "account_accountant",
    ],
    "data": ["views/account_move_line.xml"],
    "pre_init_hook": "pre_init_hook",
    "demo": [],
}
