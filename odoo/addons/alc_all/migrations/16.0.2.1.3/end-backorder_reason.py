# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _set_reception_backorder(env):
    reception = env.ref("stock.picking_type_in")
    reception.write(
        {
            "backorder_reason": True,
            "backorder_reason_purchase": True,
        }
    )


@openupgrade.migrate()
def migrate(env, version):
    _set_reception_backorder(env)
