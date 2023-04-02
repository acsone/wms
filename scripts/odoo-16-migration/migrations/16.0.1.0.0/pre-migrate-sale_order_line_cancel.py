# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr,
        "sale.order.line",
        ["product_qty_canceled", "product_qty_remains_to_deliver"],
        "sale_cancel_remaining",
        "sale_order_line_cancel",
    )
