# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version=None):
    """Fill product_width and product_height and length on product_product."""
    _logger.info("Fill product_width and product_height and length on product_product")
    # dimension are in cm and we compute the volume in dm3
    cr.execute(
        """
        UPDATE product_product
        SET product_width = width,
            product_height = height,
            product_length = length,
            volume = width * height * length / 1000
        WHERE width IS NOT NULL and height IS NOT NULL and length IS NOT NULL
    """
    )
    _logger.info(f"{cr.rowcount} rows updated in product_product")

    _logger.info("Fill volume on product_template with volume from product_product")
    # set the volume on the template if only one variant
    cr.execute(
        """
        UPDATE product_template
        SET volume = (select volume from product_product where product_tmpl_id = product_template.id)
        WHERE id in (select product_tmpl_id from product_product group by product_tmpl_id having count(*) = 1)
    """
    )
    _logger.info(f"{cr.rowcount} rows updated in product_template")

    _logger.info("Fill volume uom on product_template")
    # set the volume uom on the product_template to liter
    cr.execute(
        """
        UPDATE product_template
        SET volume_uom_id = (select res_id from ir_model_data where module = 'uom' and name = 'product_uom_litre')
    """
    )
    _logger.info(f"{cr.rowcount} rows updated in product_template")
