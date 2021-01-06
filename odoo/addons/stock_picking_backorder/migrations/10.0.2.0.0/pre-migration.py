# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    # Move fields to alce_stock_picking_backorder_helpdesk
    openupgrade.update_module_moved_fields(
        cr,
        "stock.backorder.reason",
        ["is_helpdesk_ticket_to_create", "helpdesk_ticket_reason_id"],
        "stock_picking_backorder",
        "alce_stock_picking_backorder_helpdesk",
    )

    openupgrade.update_module_moved_fields(
        cr,
        "stock.backorder.choice",
        [
            "is_helpdesk_ticket_to_create",
            "helpdesk_ticket_reason_id",
            "helpdesk_ticket_description",
        ],
        "stock_picking_backorder",
        "alce_stock_picking_backorder_helpdesk",
    )
