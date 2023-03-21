# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_pickings_group_by(env):
    fields = [
        (
            "stock.picking.type",
            "stock_picking_type",
            "groupbypartner",
            "group_pickings",
        ),
        (
            "stock.picking.type",
            "stock_picking_type",
            "groupbypartner_maxweight",
            "group_pickings_maxweight",
        ),
    ]
    openupgrade.rename_fields(env, fields)


@openupgrade.migrate()
def migrate(env, version):
    _rename_pickings_group_by(env)
