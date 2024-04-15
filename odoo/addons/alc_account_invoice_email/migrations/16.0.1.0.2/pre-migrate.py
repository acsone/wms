# Copyright 2024 ACSONE SA/NV

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Forcing update of account.email_template_edi_credit_note")
    openupgrade.load_data(
        cr,
        "alc_account_invoice_email",
        "migrations/16.0.1.0.2/mail_template.xml",
        mode="init",
    )
