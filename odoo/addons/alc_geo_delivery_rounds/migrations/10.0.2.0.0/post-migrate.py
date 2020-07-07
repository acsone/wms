# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.alc_geo_delivery_rounds.hooks import _fill_partner_tag

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("create tags")

    _fill_partner_tag(cr)
