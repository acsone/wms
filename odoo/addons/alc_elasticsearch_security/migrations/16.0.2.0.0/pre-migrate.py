import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # unlink elasticsearch roles linked to pricelists so
    # they will be recreated fot the new role names while
    # keeping the old ones into OpenSearch

    cr.execute(
        """
        DELETE FROM elasticsearch_role WHERE pricelist_id IS NOT NULL
        """
    )
    _logger.info("Deleted elasticsearch roles linked to pricelists")
