# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Set company.external_report_layout_id which is now read only in the UX."
    )
    env.cr.execute(
        """
          UPDATE res_company
          SET external_report_layout_id = model_data.res_id
          FROM (SELECT res_id from ir_model_data
                WHERE name = 'external_layout_alcyon'
                AND module = 'alc_report_base') AS model_data
        """
    )
