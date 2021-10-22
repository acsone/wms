# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models

from .utils import create_index


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    sale_line_id = fields.Many2one(index=True)
    purchase_line_id = fields.Many2one(index=True)
    group_id = fields.Many2one(index=True)
    move_dest_id = fields.Many2one(index=True)

    @api.model_cr
    def init(self):
        # index for incoming and ongoing move in product qty compute
        index_name = "procurement_order_wip_idx"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(orderpoint_id) where state not in ('done', 'cancel')",
        )

    @api.model
    def create(self, vals):
        self_no_track = self.with_context(tracking_disable=True)
        return super(ProcurementOrder, self_no_track).create(vals)

    @api.multi
    def write(self, vals):
        self_no_track = self.with_context(tracking_disable=True)
        return super(ProcurementOrder, self_no_track).write(vals)
