# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(env):
    data = [
        (
            "specific_print.alcyon_header",
            "alc_report_base.alcyon_header",
        ),
        (
            "specific_print.page_number_footer",
            "alc_report_base.page_number_footer",
        ),
    ]
    openupgrade.rename_xmlids(env.cr, data, allow_merge=True)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_data(env)
