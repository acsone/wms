# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _rename_base_jsonify(env):
    modules = [
        (
            "base_jsonify",
            "jsonifier",
        )
    ]
    openupgrade.update_module_names(env.cr, modules, merge_modules=True)


@openupgrade.migrate()
def migrate(env, version):
    _rename_base_jsonify(env)
