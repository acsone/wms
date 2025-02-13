import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version=None):
    _logger.info("Creating 'expiration_date' field on stock.quant")
    env = api.Environment(cr, SUPERUSER_ID, {})
    field_spec = [
        (
            "expiration_date",
            "stock.quant",
            False,
            "datetime",
            "timestamp without time zone",
            "alc_stock_available_product_expiry",
        )
    ]
    openupgrade.add_fields(env, field_spec=field_spec)

    _logger.info("Populating 'expiration_date' field on stock.quant")

    sql = """
            UPDATE
                stock_quant sq
            SET
                expiration_date = sl.expiration_date
            FROM
                stock_lot sl
            WHERE
                sq.lot_id = sl.id
                AND sl.expiration_date IS NOT NULL
        """
    cr.execute(sql)
    _logger.info("%d stock quants updated", cr.rowcount)
