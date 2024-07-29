# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Invoicing Mode Split Refund",
    "description": """
        This is a extends `partner_invoicing_mode` module to enable invoicing cron jobs
        to separate refunds from invoices when invoicing sale orders.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "partner_invoicing_mode",
        # fmt: on
    ],
    "data": [],
    "demo": [],
}
