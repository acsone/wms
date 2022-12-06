# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_purchase_packaging(env):
    fields = [
        (
            "purchase.order.line",
            "purchase_order_line",
            "product_packaging",
            "product_packaging_id",
        )
    ]
    openupgrade.rename_fields(env, fields)


@openupgrade.migrate()
def migrate(env, version):
    _rename_purchase_packaging(env)
