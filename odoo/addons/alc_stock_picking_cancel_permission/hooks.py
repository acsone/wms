# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved xml_id from specific_data
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "stock_constraint.group_picking_cancel",
                "alc_stock_picking_cancel_permission.group_picking_cancel",
            )
        ],
    )
