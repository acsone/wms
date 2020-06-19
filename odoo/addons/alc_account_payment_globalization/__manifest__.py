# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Account Payment Globalization",
    "description": """

This addon provides a wizard that will allow you to transfer the debits from move lines linked to a specific payment mode and account to an other partner account by

* crediting the customer account of each veterinarian with one transaction for each invoice to be carried over to the Chronovet customer account. The entry will read: "< Invoice No. > Chronovet".
* debiting the Chronovet customer account with the total amount of the invoices to be paid.
* lettering the entries in the veterinarian's client account. lettering between the amount of the sale (Debit) and the amount transferred to the Chronovet account (Credit).


Translated with www.DeepL.com/Translator (free version)""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "account",
        "account_payment_mode",
        "account_payment_partner",  # payment_mode_id on account.invoice
    ],
    "data": ["wizards/alc_account_payment_globalization.xml"],
    "demo": [],
}
