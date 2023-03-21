# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _move_so_product_qty_unavailable_fields(env):
    _logger.info(
        "sale.order.line: move fields 'current_product_qty_unavailable' "
        "and 'product_qty_unavailable'"
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "sale.order.line",
        [
            "product_qty_unavailable",
            "current_product_qty_unavailable",
        ],
        "alc_sale_product_qty_unavailable",
        "procurement_sale",
    )


@openupgrade.migrate()
def migrate(env, version):
    _move_so_product_qty_unavailable_fields(env)
