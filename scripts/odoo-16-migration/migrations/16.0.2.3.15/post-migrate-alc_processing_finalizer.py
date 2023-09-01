# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(env):
    data = [
        (
            "__export__.mail_template_30",
            "alc_sale_processing_finalizer.mail_template_30",
        ),
    ]
    openupgrade.rename_xmlids(env.cr, data, allow_merge=True)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_data(env)
