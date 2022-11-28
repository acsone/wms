# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_abc(env):
    modules = [
        (
            "alc_product_abc_classification",
            "stock_storage_type_putaway_abc_classification_sale_stock",
        )
    ]
    openupgrade.update_module_names(env.cr, modules, merge_modules=True)


@openupgrade.migrate()
def migrate(env, version):
    _rename_abc(env)
