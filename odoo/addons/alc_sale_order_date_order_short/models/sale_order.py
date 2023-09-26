# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields

from odoo.addons.sale.models.sale_order import SaleOrder as SaleBase


class SaleOrder(SaleBase):

    date_order_short = fields.Date(compute="_compute_date_order_short")

    @api.depends("date_order")
    def _compute_date_order_short(self):
        for sale in self:
            if sale.date_order:
                sale.date_order_short = sale.date_order
