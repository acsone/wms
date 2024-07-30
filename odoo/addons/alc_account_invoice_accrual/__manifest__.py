# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "ALC account invoice accrual",
    "version": "16.0.1.0.0",
    "author": "BCIM, ACSONE SA/NV",
    "category": "Accounting & Finance",
    "depends": [
        # Custom
        "alc_base_auto_join",
        # OCA
        "account_invoice_accrual",
    ],
    "data": ["data/ir_cron.xml"],
    "license": "AGPL-3",
    "application": False,
}
