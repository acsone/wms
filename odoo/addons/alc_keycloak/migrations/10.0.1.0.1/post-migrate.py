# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Schedule keycloak attribute synchronization")
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    kusers = env["keycloak.user"].search([])
    kusers.action_sync_keycloak_info()
    return
