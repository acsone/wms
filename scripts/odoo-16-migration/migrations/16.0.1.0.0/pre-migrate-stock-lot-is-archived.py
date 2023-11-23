# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _change_column(cr):
    openupgrade.update_module_moved_fields(
        cr,
        "stock.lot",
        ("is_archived",),
        "alc_stock_production_lot_archive",
        "stock_lot_is_archived",
    )


def migrate(cr, version):
    _change_column(cr)
