# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Create sale_channel_id column on sale_order_line to avoid recompute")
    cr.execute(
        """
        ALTER TABLE sale_order_line
        ADD COLUMN sale_channel_id integer
    """
    )
