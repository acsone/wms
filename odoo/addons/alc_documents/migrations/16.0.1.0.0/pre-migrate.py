# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Create sale_channel_id column on alc_document to avoid recompute")
    cr.execute(
        """
        ALTER TABLE alc_document
        ADD COLUMN sale_channel_id integer
    """
    )
