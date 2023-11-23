# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(cr):
    data = [
        (
            "stock_picking_backorder.stock_backorder_reason_1",
            "alc_stock_picking_backorder_reason.stock_backorder_reason_1",
        ),
        (
            "stock_picking_backorder.stock_backorder_reason_2",
            "alc_stock_picking_backorder_reason.stock_backorder_reason_2",
        ),
        (
            "stock_picking_backorder.stock_backorder_reason_3",
            "alc_stock_picking_backorder_reason.stock_backorder_reason_3",
        ),
        (
            "stock_picking_backorder.stock_backorder_reason_4",
            "alc_stock_picking_backorder_reason.stock_backorder_reason_4",
        ),
    ]
    openupgrade.rename_xmlids(cr, data, allow_merge=True)


def migrate(cr, version):
    _migrate_data(cr)
