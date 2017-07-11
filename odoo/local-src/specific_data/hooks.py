# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):

    logging.getLogger('odoo.addons.specific_data').info(
        'Defining food picking type')

    env = api.Environment(cr, SUPERUSER_ID, {})

    food_picking_type = env.ref('__setup__.stock_picking_type_ali',
                                raise_if_not_found=False)
    if food_picking_type:
        food_picking_type.food_type = True
