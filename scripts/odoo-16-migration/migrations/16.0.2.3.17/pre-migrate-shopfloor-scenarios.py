# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_scenarios(env):
    xmlids = [
        (
            "alc_shopfloor.scenario_location_content_transfer",
            "shopfloor.scenario_location_content_transfer",
        ),
        (
            "alc_shopfloor.scenario_cluster_picking",
            "shopfloor.scenario_cluster_picking",
        ),
    ]

    openupgrade.rename_xmlids(env.cr, xmlids)


@openupgrade.migrate()
def migrate(env, version):
    _rename_scenarios(env)
