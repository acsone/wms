# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    scenario = env.ref("alc_shopfloor.scenario_location_content_transfer")
    options = scenario.options
    if "avoid_transfer_bin_to_reserve" in options:
        options.pop("avoid_transfer_bin_to_reserve")
    options["preserve_origin_location_kind"] = True
    env.cr.execute(
        """
    UPDATE
        shopfloor_scenario
    SET
        options_edit = %s
    WHERE
        id = %s
    """,
        (json.dumps(options), scenario.id),
    )
