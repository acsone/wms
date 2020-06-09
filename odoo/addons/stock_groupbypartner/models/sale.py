# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux (BCIM)
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends("procurement_group_id")
    def _compute_picking_ids(self):
        for order in self:
            order.picking_ids = (
                self.env["stock.move"]
                .search([("group_id", "=", order.procurement_group_id.id)])
                .mapped("picking_id")
                if order.procurement_group_id
                else []
            )
            order.delivery_count = len(order.picking_ids)

    def _prepare_procurement_group(self):
        values = super(SaleOrder, self)._prepare_procurement_group()
        values["customer_id"] = self.partner_id.id
        if self.carrier_id:
            values["carrier_id"] = self.carrier_id.id
        return values
