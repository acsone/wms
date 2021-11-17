# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref(
        "alc_shopfloor.stock_picking_type_reassort_medoc"
    ).ignore_putaway_reserve = True
    env.ref("__setup__.stock_picking_type_reassort_ali").ignore_putaway_reserve = True
