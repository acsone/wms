# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(env):
    data = [
        (
            "alc_logiweb.logiweb_partner",
            "alc_sale_processing_finalizer_exclude_logiweb.logiweb_partner",
        ),
        (
            "alc_logiweb.logiweb_be_partner",
            "alc_sale_processing_finalizer_exclude_logiweb.logiweb_be_partner",
        ),
    ]
    openupgrade.rename_xmlids(env.cr, data, allow_merge=True)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_data(env)
