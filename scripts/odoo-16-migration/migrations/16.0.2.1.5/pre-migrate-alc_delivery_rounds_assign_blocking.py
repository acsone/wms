# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.update_module_moved_fields(
        cr,
        "stock.picking",
        ["ignore_delivery_round_assign_block"],
        "alc_delivery_rounds_assign_blocking_unavailable_product",
        "alc_stock_release_channel_assign_blocking_unavailable_product",
    )
    openupgrade.rename_fields(
        cr,
        [
            (
                "stock.picking",
                "stock_picking",
                "ignore_delivery_round_assign_block",
                "ignore_release_channel_block",
            )
        ],
    )

    openupgrade.update_module_moved_fields(
        cr,
        "stock.move",
        ["delivery_requires_other_lines"],
        "alc_delivery_rounds_assign_blocking",
        "alc_stock_release_channel_assign_blocking_unavailable_product",
    )
    openupgrade.rename_fields(
        cr,
        [
            (
                "stock.picking",
                "stock_picking",
                "delivery_requires_other_lines",
                "is_backorder",
            )
        ],
    )
    openupgrade.update_module_moved_fields(
        cr,
        "stock.move",
        ["product_qty_unavailable"],
        "alc_delivery_rounds_assign_blocking_unavailable_product",
        "alc_stock_release_channel_assign_blocking_unavailable_product",
    )
