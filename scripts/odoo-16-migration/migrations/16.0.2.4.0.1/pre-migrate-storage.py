# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Rename main_image_id on product_template and product_product")
    cr.execute(
        """
            alter table product_template rename COLUMN main_image_id to  x_main_image_id;
            alter table product_template drop constraint product_template_main_image_id_fkey;
            alter table product_product rename COLUMN main_image_id to  x_main_image_id;
            alter table product_product drop constraint product_product_main_image_id_fkey;
        """
    )
    _logger.info("%s stock.package.type updated", cr.rowcount)
