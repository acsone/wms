# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_round_tag_table(cr):
    openupgrade.rename_tables(
        cr,
        [("round_tag", "alc_stock_release_channel_tag")],
    )
    openupgrade.rename_tables(
        cr,
        [
            (
                "res_partner_round_tag_rel",
                "res_partner_stock_release_channel_tag_rel",
            )
        ],
    )
    openupgrade.rename_columns(
        cr,
        {
            "res_partner_stock_release_channel_tag_rel": [
                ("round_tag_id", "alc_stock_release_channel_tag_id")
            ]
        },
    )


def migrate(cr, version):
    _rename_round_tag_table(cr)
