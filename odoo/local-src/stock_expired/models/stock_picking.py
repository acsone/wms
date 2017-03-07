# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    to_process_quant_expired = fields.Boolean(
        'Bypass restriction on expired quants')
