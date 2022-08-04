# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.load_data(
        cr, "account_invoice_email", "data/mail_template.xml", mode="init"
    )
