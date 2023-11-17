# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def _migrate_shopinvader_product_url(cr):
    """Migrate the url_url table for shopinvader.product records."""

    # in the table url_url, we have a field model_id that is a reference to
    # the model of the object linked to the url. We are interested in the
    # records where model_id starts with shopinvader.product
    # When splitting the model_id on ',' the second part is the id of the
    # record in shopinvader_product table.
    # For each row, we must fill the res_id, res_model and manual columns
    # with the value coming from the shopinvader_product table.
    # * res_id  is the record_id column of the shopinvader_product table
    # * res_model is always 'product.template'
    # * manual is False if the shopinvader_product.url_builder is 'auto' and True otherwise
    _logger.info("Migrate url_url for shopinvader.product records")
    cr.execute(
        """
        UPDATE
            url_url url
        SET
            key = url.url_key,
            res_id = shopinvader_product.record_id,
            res_model = 'product.template',
            manual = shopinvader_product.url_builder = 'manual'
        FROM
            shopinvader_product
        WHERE
            url.model_id LIKE 'shopinvader.product,%'
            AND url.res_id IS NULL
            AND url.res_model IS NULL
            AND shopinvader_product.id = CAST(SPLIT_PART(url.model_id, ',', 2) AS INTEGER)
        """
    )
    _logger.info("%s url_url for shopinvader.product records migrated", cr.rowcount)


def _migrate_shopinvader_category_url(cr):
    _logger.info("Migrate url_url for shopinvader.category records")
    cr.execute(
        """
        UPDATE
            url_url url
        SET
            key = url.url_key,
            res_id = shopinvader_category.record_id,
            res_model = 'product.category',
            manual = shopinvader_category.url_builder = 'manual'
        FROM
            shopinvader_category
        WHERE
            url.model_id LIKE 'shopinvader.category,%'
            AND url.res_id IS NULL
            AND url.res_model IS NULL
            AND shopinvader_category.id = CAST(SPLIT_PART(url.model_id, ',', 2) AS INTEGER)
        """
    )
    _logger.info("%s url_url for shopinvader.category records migrated", cr.rowcount)


def migrate(cr, version):
    _migrate_shopinvader_product_url(cr)
    _migrate_shopinvader_category_url(cr)
