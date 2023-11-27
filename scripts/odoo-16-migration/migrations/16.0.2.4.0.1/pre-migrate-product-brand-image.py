# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Rename image_id on product_brand")
    cr.execute(
        """
            alter table product_brand rename COLUMN image_id to  x_image_id;
        """
    )
