import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # unlink elasticsearch roles linked to veterinary group so
    # they will be recreated fot the new role names while
    # keeping the old ones into OpenSearch

    cr.execute(
        """
        DELETE FROM elasticsearch_role WHERE vt_group_id IS NOT NULL
        """
    )
    _logger.info("Deleted elasticsearch roles linked to veterinary group")
