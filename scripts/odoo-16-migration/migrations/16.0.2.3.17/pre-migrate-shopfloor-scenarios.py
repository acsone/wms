# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_scenarios(cr):
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

    openupgrade.rename_xmlids(cr, xmlids)


def migrate(cr, version):
    _rename_scenarios(cr)
