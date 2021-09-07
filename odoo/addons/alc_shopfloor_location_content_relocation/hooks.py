# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Loaded after installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    scenario = env.ref("alc_shopfloor.scenario_location_content_transfer")
    options = scenario.options
    options["avoid_transfer_bin_to_reserve"] = True
    scenario.options_edit = json.dumps(options)

    env.ref(
        "alc_shopfloor.shopfloor_menu_medoc_relocation"
    ).avoid_transfer_bin_to_reserve = True
