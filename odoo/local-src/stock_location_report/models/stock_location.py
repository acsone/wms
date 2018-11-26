# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from itertools import groupby
from collections import OrderedDict

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    color = fields.Selection([
        ('blue', 'Blue'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ], string="Color")

    def _get_by_position(self, field, reverse=False):
        def key(r):
            return r[field]
        res = OrderedDict((k, self.browse(x.id for x in g)) for k, g in groupby(
            self.sorted(key, reverse=reverse), key=key))
        return res
