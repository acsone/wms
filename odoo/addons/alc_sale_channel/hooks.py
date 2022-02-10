# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from alc_sale_channel_stock_move
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order.line",
        ["sale.channel"],
        "alc_sale_channel_stock_move",
        "alc_sale_channel",
    )

    # Moved fields from specific_sale
    openupgrade.update_module_moved_fields(
        cr, "sale.order", ["sale.channel"], "specific_sale", "alc_sale_channel"
    )
