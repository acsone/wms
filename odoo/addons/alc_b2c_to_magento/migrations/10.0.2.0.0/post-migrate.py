# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    modules_to_uninstall = ["alc_placedesvetos_to_magento", "alc_chronovet_to_magento"]
    _logger.info("Uninstall specific magento modules.")
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env["ir.module.module"].search([("name", "in", modules_to_uninstall)])
    if module:
        module.write({"state": "to remove"})
