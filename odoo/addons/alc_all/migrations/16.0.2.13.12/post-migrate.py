import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version=None):
    if version is None:
        return
    # disable check connection method by default to avoid trouble between
    # the different environments
    cr.execute("UPDATE fs_storage set check_connection_method=null")
    _logger.info(
        "Disable check connection method by default on %s storage(s)", cr.rowcount
    )
