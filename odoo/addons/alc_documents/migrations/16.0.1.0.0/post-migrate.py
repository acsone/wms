# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set sale channels")
    cr.execute(
        """
        UPDATE alc_document SET
        sale_channel_id=sale_channel.id
        FROM sale_channel
        WHERE alc_document.sale_channel=sale_channel.code
    """
    )
