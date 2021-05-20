# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        for po in self:
            for line in po.order_line:
                line.date_announced = po.date_planned

        return super(PurchaseOrder, self).button_confirm()
