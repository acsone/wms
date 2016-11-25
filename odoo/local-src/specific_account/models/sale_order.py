# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_order_short = fields.Date(compute='_compute_date_order_short')

    @api.depends('date_order')
    def _compute_date_order_short(self):
        for sale in self:
            if sale.date_order:
                sale.date_order_short = datetime.strptime(
                    sale.date_order, DEFAULT_SERVER_DATETIME_FORMAT
                ).date()
