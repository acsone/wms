# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(env):
    fields = [
        (
            "stock.location",
            "product_template",
            "keep_track_of_delivery_round",
            "keep_track_of_release_channel",
        ),
        (
            "stock.location",
            "product_template",
            "delivery_round_id",
            "release_channel_id",
        ),
    ]
    openupgrade.rename_fields(env, fields)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_data(env)
