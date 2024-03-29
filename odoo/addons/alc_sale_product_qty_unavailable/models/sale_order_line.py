# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.sale_order_line_cancel.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):

    date_order = fields.Datetime(related="order_id.date_order", readonly="True")

    current_product_qty_unavailable = fields.Float(
        string="Current quantity unavailable",
        digits="Product Unit of Measure",
        compute="_compute_current_product_qty_unavailable",
    )

    product_qty_unavailable = fields.Float(
        string="Quantity unavailable",
        digits="Product Unit of Measure",
        readonly=True,
        copy=False,
    )

    @api.model
    def get_product_qty_unavailable(self, product, product_uom_qty, confirmed, line_id):
        if product and product_uom_qty:
            if product.type == "service":
                return 0
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
                # Because ordered quantity is already
                # computed in immediately usable quantity,
                # if immediately usable quantity is negative,
                # the unavailable quantity
                # equals the immediately usable quantity
                # minus the sum of stock move quantity
                # which stock move is after the order line stock move
                StockMove = self.env["stock.move"]
                order_line_stock_move = StockMove.search(
                    [
                        ("sale_line_id", "=", line_id),
                        ("state", "not in", ["draft", "cancel", "done"]),
                    ],
                    limit=1,
                )
                if not order_line_stock_move:
                    return min(abs(immediately_usable_qty), product_uom_qty)
                stock_move_date_deadline = order_line_stock_move.date_deadline
                with StockMove._auto_join(["location_id", "location_dest_id"]):
                    next_stock_moves = self.env["stock.move"].search(
                        [
                            ("product_id", "=", product.id),
                            ("location_id.usage", "in", ("internal", "view")),
                            ("location_dest_id.usage", "=", "customer"),
                            ("sale_line_id", "!=", line_id),
                            ("state", "not in", ["draft", "cancel", "done"]),
                            "|",
                            "|",
                            ("priority", "<", order_line_stock_move.priority),
                            "&",
                            ("priority", "=", order_line_stock_move.priority),
                            ("date_deadline", ">", stock_move_date_deadline),
                            # in rare case of same date_dealine,
                            # use id to sort the moves
                            "&",
                            "&",
                            ("priority", "=", order_line_stock_move.priority),
                            ("date_deadline", "=", stock_move_date_deadline),
                            ("id", ">", order_line_stock_move.id),
                        ]
                    )
                next_quantities = sum(move.product_uom_qty for move in next_stock_moves)

                good_immediately_usable_qty = immediately_usable_qty + next_quantities

                if good_immediately_usable_qty <= 0:
                    return min(product_uom_qty, abs(good_immediately_usable_qty))
                return 0
            # If sale order line is NOT confirmed, ordered quantity
            # is NOT already computed in immediately usable quantity
            if immediately_usable_qty <= 0:
                # If immediately usable quantity is negative,
                # the unavailable quantity equals the sum
                # between ordered quantity
                # and immediately usable quantity absolute value
                return product_uom_qty
            # If immediately usable quantity is positive,
            # the unavailable quantity equals the ordered quantity
            # minus the immediately usable quantity
            # (limited with ordered quantity)
            return max(product_uom_qty - immediately_usable_qty, 0)
        return None

    @api.onchange(
        "product_id",
        "product_uom_qty",
        "route_id",
        "order_id",
        "date_order",
    )
    def onchange_for_product_qty_unavailable(self):
        for line in self:
            if (
                not line.product_id
                or not line.product_uom_qty
                or not line.order_id.date_order
            ):
                line.product_qty_unavailable = None
                continue
            line.product_qty_unavailable = line.get_product_qty_unavailable(
                # context change to get the corrections of immediately
                # available qty with the date
                line.product_id.with_context(date=line.order_id.date_order),
                line.product_uom_qty,
                line.state in ("sale", "done"),
                None,
            )

    def _init_product_qty_unavailable(self, vals):
        """
        This method is used as a kind of trick to avoid undesirable recompute of.

        the product_qty_unavailable
        """
        # don't trigger product_qty_unavalable computation if the value is provided.
        if vals.get("product_uom_qty") and "product_qty_unavailable" not in vals:
            # Because product_qty_unavailable is readonly and not computed, we need
            # to apply the onchange on create / save to save the correct values.
            self.onchange_for_product_qty_unavailable()
        return self

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record, vals in zip(res, vals_list, strict=False):
            record._init_product_qty_unavailable(vals)
        return res

    def write(self, values):
        result = super().write(values)
        self._init_product_qty_unavailable(values)
        return result

    def _compute_current_product_qty_unavailable(self):
        for line in self:
            if not line.product_qty_remains_to_deliver:
                continue
            line.current_product_qty_unavailable = min(
                self.get_product_qty_unavailable(
                    # context change to get the corrections of immediately
                    # available qty with the date
                    line.product_id,
                    line.product_uom_qty,
                    line.state == "sale",
                    line.id,
                ),
                line.product_qty_remains_to_deliver,
            )

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id=group_id)
        values["product_qty_unavailable"] = self.product_qty_unavailable
        return values
