# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(cr):
    """Rename at first install the former picking type aliment."""
    aliment = [
        (
            "__setup__.stock_picking_type_ali",
            "alc_stock_picking_type_aliment.stock_picking_type_ali",
        )
    ]
    openupgrade.rename_xmlids(cr, aliment, allow_merge=True)


def pre_init_hook(cr):
    _migrate_data(cr)
