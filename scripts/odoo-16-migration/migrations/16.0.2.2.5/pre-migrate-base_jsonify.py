# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _rename_base_jsonify(cr):
    modules = [
        (
            "base_jsonify",
            "jsonifier",
        )
    ]
    openupgrade.update_module_names(cr, modules, merge_modules=True)


def migrate(cr, version):
    _rename_base_jsonify(cr)
