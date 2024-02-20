# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _init_blocked_field(env):
    """Initialize blocked_for_channel_assignation field."""
    field_spec = [
        (
            "blocked_for_channel_assignation",
            "stock.picking",
            False,
            "boolean",
            "boolean",
            "alc_stock_release_channel_blocking_unavailable_product",
        )
    ]
    openupgrade.add_fields(env, field_spec=field_spec)


@openupgrade.migrate()
def migrate(env, version):
    _init_blocked_field(env)
