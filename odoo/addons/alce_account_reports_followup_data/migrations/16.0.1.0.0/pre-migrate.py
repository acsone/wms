# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _create_new_xmlids(cr):
    _logger.info(
        "Create xmlids for mail_templates that were created durirng odoo "
        "migration of the old followup_lines"
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    for i in (1, 2):
        followup_line = env.ref(
            f"alce_account_reports_followup_data.alcyon_followup_line{i}"
        )
        openupgrade.add_xmlid(
            cr,
            module="alce_account_reports_followup_data",
            xmlid=f"alcyon_email_template_followup_{i}",
            model="mail.template",
            res_id=followup_line.mail_template_id.id,
            noupdate=True,
        )


def migrate(cr, version):
    _create_new_xmlids(cr)
