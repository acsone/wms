# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Uninstall module db2_import")
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    roles = env["elasticsearch.role"].search([])
    for role in roles:
        domain = [("role_name", "=", role.name)]
        pricelist = env["product.pricelist"].search(domain)
        if pricelist:
            role.pricelist_id = pricelist
