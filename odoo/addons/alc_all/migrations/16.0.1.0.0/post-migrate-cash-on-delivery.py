# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_abc(env):
    modules = [
        (
            "cash_on_delivery",
            "alc_cash_on_delivery",
        )
    ]
    openupgrade.update_module_names(env.cr, modules, merge_modules=True)


@openupgrade.migrate()
def migrate(env, version):
    _rename_abc(env)
