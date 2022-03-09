# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    scenario = env.ref("alc_shopfloor.scenario_cluster_picking")
    options = scenario.options
    options["scan_workstation"] = True
    scenario.options_edit = json.dumps(options)
