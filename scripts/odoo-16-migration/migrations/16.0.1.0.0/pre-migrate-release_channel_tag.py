# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_round_tag_table(env):
    openupgrade.rename_tables(
        env.cr,
        [("round_tag", "alc_stock_release_channel_tag")],
    )


@openupgrade.migrate()
def migrate(env, version):
    _rename_round_tag_table(env)
