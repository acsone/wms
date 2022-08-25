# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    is_human_order_line = fields.Boolean(
        compute="_compute_is_human_order_line", store=True
    )

    @api.depends("product_id", "product_id.product_tmpl_id")
    def _compute_is_human_order_line(self):
        for rec in self:
            rec.is_human_order_line = rec.product_id.product_tmpl_id.is_human

    def _prepare_order_line_procurement(self, group_id):
        self.ensure_one()
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id
        )
        vals["do_not_deliver_line"] = (
            self.order_id.do_not_deliver_if_alone or self.is_human_order_line
        )
        return vals
