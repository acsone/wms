# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

IDS = {
    "stock_pick_packs_label_zebra_v1",
}


def migrate(cr, version):
    # set labels we want to update to noupdate=False
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data
        SET noupdate=false
        WHERE module='alc_label_printing_base'
        AND name IN %s
    """,
        (tuple(IDS),),
    )
