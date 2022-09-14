# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("uninstall 'camptocamp_tools', 'csv_file_export', 'csv_file_import'")
    cr.execute(
        "update ir_module_module set state = 'to remove' where name in ('camptocamp_tools', 'csv_file_export', 'csv_file_import')"
    )
