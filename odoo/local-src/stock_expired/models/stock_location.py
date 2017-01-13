# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    ignore_quants_expiration = fields.Boolean(
        string='Ignore quants expiration',
    )
