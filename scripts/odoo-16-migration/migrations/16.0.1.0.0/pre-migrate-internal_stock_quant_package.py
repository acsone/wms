# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _move_stock_quant_package(cr):
    _logger.info("stock.quant.package: move field 'is_internal'")
    openupgrade.update_module_moved_fields(
        cr,
        "stock.quant.package",
        ["is_internal"],
        "alc_internal_stock_quant_package",
        "internal_stock_quant_package",
    )


def _move_stock_picking(cr):
    _logger.info("stock.picking: move field 'empty_internal_package_on_transfer'")
    openupgrade.update_module_moved_fields(
        cr,
        "stock.picking",
        ["empty_internal_package_on_transfer"],
        "alc_internal_stock_quant_package",
        "internal_stock_quant_package",
    )


def _move_stock_picking_type(cr):
    _logger.info(
        "stock.picking.type: move fields 'empty_internal_package_on_transfer' "
        "and 'stock_internal_package_config_line_ids'"
    )
    openupgrade.update_module_moved_fields(
        cr,
        "stock.picking.type",
        [
            "empty_internal_package_on_transfer",
            "stock_internal_package_config_line_ids",
        ],
        "alc_internal_stock_quant_package",
        "internal_stock_quant_package",
    )


def _move_stock_internal_package_config_line(cr):
    _logger.info(
        "stock.internal.package.config.line: move fields 'empty', "
        "'delivery_carrier_id' and 'stock_picking_type_id'"
    )
    openupgrade.update_module_moved_fields(
        cr,
        "stock.picking.type",
        [
            "empty",
            "delivery_carrier_id",
            "stock_picking_type_id",
        ],
        "alc_internal_stock_quant_package",
        "internal_stock_quant_package",
    )


def migrate(cr, version):
    _move_stock_picking(cr)
    _move_stock_picking_type(cr)
    _move_stock_quant_package(cr)
    _move_stock_internal_package_config_line(cr)
