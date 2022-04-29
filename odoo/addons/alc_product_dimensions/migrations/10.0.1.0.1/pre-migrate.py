# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_product_dimensions.hooks import pre_init_hook


def migrate(cr, version):
    pre_init_hook(cr)
