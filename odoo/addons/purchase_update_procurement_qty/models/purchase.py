# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, models
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.constrains("product_qty")
    def _check_qty_procurement(self):
        """check that the purchased qty is greater than the qty comming from MTO
        procurements"""
        for rec in self:
            mto_qty = rec._get_mto_qty()
            if mto_qty > rec.product_qty:
                raise exceptions.ValidationError(
                    _(
                        "You cannot decrease the purchased quantity of product "
                        "%s below %s %s, which is the quantity requested by "
                        "Make To Order procurements."
                    )
                    % (rec.product.name, mto_qty, rec.product_uom.name)
                )

    def _get_mto_qty(self):
        self.ensure_one()
        mto_procurements = self.procurement_ids.filtered(
            lambda rec: not rec.orderpoint_id
        )
        proc_qty = 0.0
        for proc in mto_procurements:
            proc_qty += proc.product_uom._compute_quantity(
                proc.product_qty, self.product_uom
            )
        return proc_qty

    def _create_stock_moves(self, picking):
        moves = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for move in moves:
            rounding = move.product_uom.rounding
            if (
                float_compare(
                    move.product_uom_qty,
                    move.procurement_id.product_qty,
                    precision_rounding=rounding,
                )
                < 0
            ):
                # we decreased the qty below the procurement's qty
                if move.procurement_id.orderpoint_id:
                    move.procurement_id.product_qty = move.product_uom_qty
        return moves
