# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info('Remove customer instance on delivery round that are empty')

    env = api.Environment(cr, SUPERUSER_ID, {})
    instances = env['round.instance.customer'].search(
        [('picking_ids', '=', False)]
    )
    instances.unlink()

    pickings = env['stock.picking'].search(
        [('delivery_round_customer_id', '!=', False), ('state', '=', 'cancel')]
    )
    instances = pickings.mapped('delivery_round_customer_id')
    instances._remove_if_empty()

    return
