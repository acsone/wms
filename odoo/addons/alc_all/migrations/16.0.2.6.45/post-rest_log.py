# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("fix rest log state")
    cr.execute(
        "UPDATE rest_log SET state='success' WHERE exception_name is null and state='failed'"
    )
