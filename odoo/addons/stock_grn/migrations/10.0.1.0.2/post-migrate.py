# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set carrier flag on partner")
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("select distinct carrier_id from stock_grn")
    ids = [r[0] for r in cr.fetchall()]
    env["res.partner"].browse(ids).write({"is_carrier": True})
