# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    data = [
        (
            "alc_search_engine.elasticsearch_backend",
            "alc_search_engine_backend.elasticsearch_backend",
        )
    ]
    openupgrade.rename_xmlids(cr, data, allow_merge=True)
