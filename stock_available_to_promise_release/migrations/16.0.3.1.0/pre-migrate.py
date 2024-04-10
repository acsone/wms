# Copyright 2024 ACSONE SA/NV (https://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Use the default sql query instead relying on ORM as all records will
    be updated.
    """
    if not openupgrade.column_exists(env.cr, "stock_picking", "release_policy"):
        field_spec = [
            (
                "release_policy",
                "stock.picking",
                False,
                "selection",
                False,
                "stock_available_to_promise_release",
                "direct",
            )
        ]
        openupgrade.add_fields(env, field_spec=field_spec)
