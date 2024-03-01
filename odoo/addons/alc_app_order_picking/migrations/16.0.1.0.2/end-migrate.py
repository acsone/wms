# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Uninstall the stock_inventory module")
    module = env["ir.module.module"].search([("name", "=", "stock_inventory")])
    module.write({"state": "to remove"})
    _logger.info("Reload quant menus delteted by the stock_inventory module")
    openupgrade.load_xml(
        cr=env.cr, module_name="stock", filename="views/stock_quant_views.xml"
    )
