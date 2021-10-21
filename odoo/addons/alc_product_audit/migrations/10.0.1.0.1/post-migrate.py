# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Update has no_dimensions / has no_packaging_dimension on products")
    if not version:
        return

    env["product.template"].search([])._compute_has_no_dimensions()
    env["product.template"].search([])._compute_packaging_has_no_dimensions()
