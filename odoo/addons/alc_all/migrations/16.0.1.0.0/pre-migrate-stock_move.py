# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_fields(env):
    fields = [
        (  # from migration/replacement of stock_delivery_note
            "stock.move",
            "stock_move",
            "order_line_id",
            "sale_line_id",
        )
    ]
    openupgrade.rename_fields(env, fields)


@openupgrade.migrate()
def migrate(env, version):
    _rename_fields(env)
