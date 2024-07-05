# Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    scenario = env["shopfloor.scenario"].search(
        [("key", "=", "location_content_transfer")]
    )
    _update_scenario_options(scenario)


def _update_scenario_options(scenario):
    options = scenario.options
    options["model_additional_domain_get_work"] = "stock.picking"
    options["allow_custom_sort_key_get_work"] = True
    options_edit = json.dumps(options or {}, indent=4, sort_keys=True)
    scenario.write({"options_edit": options_edit})
    _logger.info(
        "Option 'model_additional_domain_get_work' added to scenario Zone Picking"
    )
