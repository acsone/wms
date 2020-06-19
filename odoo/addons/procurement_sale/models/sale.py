# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirmation_date = fields.Datetime(copy=False)

    @api.multi
    def action_confirm(self):
        # Keep the confirmation date to avoid that Odoo overwrite this date
        confirmation_dates = {}
        for order in self:
            if order.confirmation_date:
                confirmation_dates[order.id] = order.confirmation_date

        result = super(SaleOrder, self).action_confirm()

        for order in self:
            if order.id in confirmation_dates:
                order.confirmation_date = confirmation_dates[order.id]

        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order = fields.Datetime(related="order_id.date_order", readonly="True")

    current_product_qty_unavailable = fields.Float(
        string="Current quantity unavailable",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_current_product_qty_unavailable",
    )

    @api.model
    def get_product_qty_unavailable(self, product, product_uom_qty, confirmed, line_id):
        if product and product_uom_qty:
            immediately_usable_qty = product.immediately_usable_qty
            if confirmed:
                # If sale order line confirmed, ordered quantity
                # is already computed in immediately usable quantity
                if immediately_usable_qty >= 0:
                    # Because ordered quantity is already
                    # computed in immediately usable quantity,
                    # if immediately usable quantity is positive,
                    # the unavailable quantity equals 0
                    return 0
                else:
                    # Because ordered quantity is already
                    # computed in immediately usable quantity,
                    # if immediately usable quantity is negative,
                    # the unavailable quantity
                    # equals the immediately usable quantity
                    # minus the sum of stock move quantity
                    # which stock move is after the order line stock move
                    StockMove = self.env["stock.move"]
                    with StockMove._auto_join(["procurement_id"]):
                        order_line_stock_move = StockMove.search(
                            [
                                ("procurement_id.sale_line_id", "=", line_id),
                                ("state", "not in", ["draft", "cancel", "done"]),
                            ],
                            limit=1,
                        )
                    if not order_line_stock_move:
                        return min(abs(immediately_usable_qty), product_uom_qty)
                    stock_move_date_expected = order_line_stock_move.date_expected
                    with StockMove._auto_join(
                        ["location_id", "location_dest_id", "procurement_id"]
                    ):
                        next_stock_moves = self.env["stock.move"].search(
                            [
                                ("product_id", "=", product.id),
                                ("location_id.usage", "in", ("internal", "view")),
                                ("location_dest_id.usage", "=", "customer"),
                                ("procurement_id.sale_line_id", "!=", line_id),
                                ("state", "not in", ["draft", "cancel", "done"]),
                                "|",
                                "|",
                                ("priority", "<", order_line_stock_move.priority),
                                "&",
                                ("priority", "=", order_line_stock_move.priority),
                                ("date_expected", ">", stock_move_date_expected),
                                # in rare case of same date_expected,
                                # use id to sort the moves
                                "&",
                                "&",
                                ("priority", "=", order_line_stock_move.priority),
                                ("date_expected", "=", stock_move_date_expected),
                                ("id", ">", order_line_stock_move.id),
                            ]
                        )
                    next_quantities = sum(
                        move.product_uom_qty for move in next_stock_moves
                    )

                    good_immediately_usable_qty = (
                        immediately_usable_qty + next_quantities
                    )

                    if good_immediately_usable_qty <= 0:
                        return min(product_uom_qty, abs(good_immediately_usable_qty))
                    else:
                        return 0
            else:
                # If sale order line is NOT confirmed, ordered quantity
                # is NOT already computed in immediately usable quantity
                if immediately_usable_qty <= 0:
                    # If immediately usable quantity is negative,
                    # the unavailable quantity equals the sum
                    # between ordered quantity
                    # and immediately usable quantity absolute value
                    return product_uom_qty
                else:
                    # If immediately usable quantity is positive,
                    # the unavailable quantity equals the ordered quantity
                    # minus the immediately usable quantity
                    # (limited with ordered quantity)
                    return max(product_uom_qty - immediately_usable_qty, 0)
        else:
            return None

    @api.onchange("product_id", "product_uom_qty", "route_id", "date_order")
    def onchange_for_product_qty_unavailable(self):
        context = self.env.context or {}
        if context.get("must_compute_product_qty_unavailable"):
            for line in self:
                line.product_qty_unavailable = line.get_product_qty_unavailable(
                    # context change to get the corrections of immediately
                    # available qty with the date and priority
                    line.product_id.with_context(
                        prio=line.route_id.priority or "1",
                        date=line.order_id.date_order,
                    ),
                    line.product_uom_qty,
                    line.state == "sale",
                    None,
                )

    @api.multi
    def write(self, values):
        """ If the route has changed, we need to adapt the procurement. Cancel
        it and recreate it """
        changed_lines = False
        if "route_id" in values:
            changed_lines = self.filtered(lambda r: r.state == "sale")
            if changed_lines:
                changed_lines.mapped("procurement_ids").cancel()
                changed_lines.mapped("procurement_ids").write({"sale_line_id": False})
                if "product_uom_qty" in values:
                    # then procurement is already recreated in standard
                    precision = self.env["decimal.precision"].precision_get(
                        "Product Unit of Measure"
                    )
                    changed_lines -= self.filtered(
                        lambda r: r.state == "sale"
                        and float_compare(
                            r.product_uom_qty,
                            values["product_uom_qty"],
                            precision_digits=precision,
                        )
                        == -1
                    )
        result = super(SaleOrderLine, self).write(values)
        if changed_lines:
            changed_lines._action_procurement_create()
        return result

    @api.multi
    def _prepare_order_line_procurement(self, group_id):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id
        )
        if not self.order_id.confirmation_date:
            raise UserError(
                _(
                    "Missing sale order confirmation date. "
                    "Cannot plan delivery procurement order"
                )
            )
        vals["date_planned"] = self.order_id.confirmation_date
        if self.route_id.priority:
            vals["priority"] = self.route_id.priority
        return vals

    def _compute_current_product_qty_unavailable(self):
        for line in self:
            if not line.product_qty_remains_to_deliver:
                continue
            line.current_product_qty_unavailable = min(
                self.get_product_qty_unavailable(
                    # context change to get the corrections of immediately
                    # available qty with the date and priority
                    line.product_id.with_context(prio=line.route_id.priority or "1"),
                    line.product_uom_qty,
                    line.state == "sale",
                    line.id,
                ),
                line.product_qty_remains_to_deliver,
            )
