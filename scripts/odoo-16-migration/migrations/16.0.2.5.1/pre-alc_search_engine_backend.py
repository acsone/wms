# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    data = [
        (
            "alc_search_engine.elasticsearch_backend",
            "alc_search_engine_backend.elasticsearch_backend",
        )
    ]
    openupgrade.rename_xmlids(env.cr, data, allow_merge=True)
