# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _set_vlb_orderpoint(env):
    """Set VLB as destination of orderpoints."""

    vlb = env.ref("alc_stock_location_data.stock_location_vlb")
    orderpoints_to_delete = (
        env["stock.warehouse.orderpoint"]
        .with_context(active_test=False)
        .search([("location_id", "=", vlb.id), ("active", "=", False)])
    )
    orderpoints_to_delete.unlink()
    orderpoints = env["stock.warehouse.orderpoint"].search(
        [("location_id", "!=", vlb.id)]
    )
    orderpoints.write(
        {
            "location_id": vlb.id,
        }
    )


@openupgrade.migrate()
def migrate(env, version):
    _set_vlb_orderpoint(env)
