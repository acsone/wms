# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    modules = [
        (
            "stock_picking_sequence",
            "alc_stock_picking_rank",
        )
    ]
    openupgrade.update_module_names(cr, modules, merge_modules=True)
