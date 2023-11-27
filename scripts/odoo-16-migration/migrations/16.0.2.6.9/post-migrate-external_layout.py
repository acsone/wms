# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate_external_layout(cr):
    _logger.info(
        "Set company.external_report_layout_id which is now read only in the UX."
    )
    cr.execute(
        """
          UPDATE res_company
          SET external_report_layout_id = model_data.res_id
          FROM (SELECT res_id from ir_model_data
                WHERE name = 'external_layout_alcyon'
                AND module = 'alc_report_base') AS model_data
        """
    )


def migrate(cr, version):
    migrate_external_layout(cr)
