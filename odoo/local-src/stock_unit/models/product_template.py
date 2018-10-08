# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unit_in_pallet = fields.Integer('Unit in pallet')
    unit_in_box = fields.Integer('Unit in box')
    unit_in_shrink_wrap = fields.Integer('Unit in shrink-wrap')
