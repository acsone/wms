# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Recompute the length on the product packaging."""
    _logger.info("Recompute the length on the product packaging.")
    cr.execute(
        """
            UPDATE
                product_packaging
            SET
                packaging_length = lngth,
                displayed_length = lngth / 10
            WHERE
                lngth is not null;
        """
    )
    _logger.info("%s product packaging updated", cr.rowcount)
