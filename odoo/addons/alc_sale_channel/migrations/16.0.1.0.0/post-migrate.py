# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set sale channels")
    cr.execute(
        """
        UPDATE sale_order SET
        sale_channel_id=sale_channel.id
        FROM sale_channel
        WHERE sale_order.sale_channel=sale_channel.code
    """
    )
    cr.execute(
        """
        UPDATE sale_order_line SET
        sale_channel_id=sale_order.sale_channel_id
        FROM sale_order
        WHERE sale_order_line.order_id=sale_order.id
    """
    )
