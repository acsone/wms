# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(env):
    data = [
        (
            "specific_account.tax_group_apb",  # used in reports only
            "alc_accounting_data.tax_group_apb",
        ),
    ]
    openupgrade.rename_xmlids(env.cr, data, allow_merge=True)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_data(env)
