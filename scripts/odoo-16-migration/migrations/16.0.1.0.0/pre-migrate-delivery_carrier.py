# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _move_maximum_weight_per_package(cr):
    _logger.info("delivery_carrier: move field maximum_weight_per_package")
    # Moved field from alc_product_audit
    openupgrade.update_module_moved_fields(
        cr,
        "delivery.carrier",
        ["maximum_weight_per_package"],
        "alc_stock_picking_number_package",
        "delivery_estimated_package_quantity_by_weight",
    )


def migrate(cr, version):
    _move_maximum_weight_per_package(cr)
