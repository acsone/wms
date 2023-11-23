# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(cr):
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
    openupgrade.rename_fields(cr, fields)


def migrate(cr, version):
    _migrate_data(cr)
