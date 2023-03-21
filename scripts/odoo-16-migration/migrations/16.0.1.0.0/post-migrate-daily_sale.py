# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_daily_sale(env):
    modules = [
        (
            "alc_product_average_daily_sale",
            "stock_average_daily_sale",
        )
    ]
    openupgrade.update_module_names(env.cr, modules, merge_modules=True)


@openupgrade.migrate()
def migrate(env, version):
    _rename_daily_sale(env)
