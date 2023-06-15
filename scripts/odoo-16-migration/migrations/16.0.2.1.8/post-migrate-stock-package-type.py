# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set flag isnew on stock.package.type with name like 'Nouveau'")
    cr.execute(
        """
            UPDATE
                stock_package_type
            SET
                is_new = True
            WHERE
                name ilike '%nouve%';
        """
    )
    _logger.info("%s stock.package.type updated", cr.rowcount)
