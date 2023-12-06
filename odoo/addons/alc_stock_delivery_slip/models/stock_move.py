# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import fields

from odoo.addons.sale_stock.models import stock
from odoo.addons.sale_stock.models.sale_order import SaleOrder


class StockMove(stock.StockMove):
    order_id = fields.Many2one[SaleOrder](related="sale_line_id.order_id")
    suite_name = fields.Char(compute="_compute_suite_name")

    def get_lots(self):
        """
        Return all lots for the stock move.

        :return: Return a list of tuple
        """
        qty_by_lot = {}

        lines = self.move_line_ids
        for line in lines:
            if not line.lot_id:
                qty_by_lot[None] = [qty_by_lot.get(None, [0])[0] + line.qty_done, ""]
                continue
            lot = line.lot_id

            existing_qty = qty_by_lot.get(lot.name, [])
            if existing_qty:
                qty_by_lot[lot.name] = [
                    existing_qty[0] + line.qty_done,
                    existing_qty[1],
                ]
            else:
                qty_by_lot[lot.name] = [line.qty_done, lot.expiration_date or ""]

        result = [[key, value[0], value[1]] for key, value in qty_by_lot.items()]

        # Sort lot by name
        return sorted(result, key=lambda lot: lot[0])

    def _compute_suite_name(self):
        for move in self:
            move.suite_name = move._get_suite_name()

    def _get_suite_name(self, sale_order=None, delivery_date=None):
        """Compute last column of the delivery note.

        Don't know what it is called but it is also found on the
        deliverslip report.
        """
        self.ensure_one()
        if not sale_order:
            sale_order = self.order_id
        if not delivery_date:
            delivery_date = self.picking_id.date_done or self.picking_id.date
        customer = sale_order.partner_id
        depot_number = customer.vet_depot_number or customer.parent_id.vet_depot_number
        if not depot_number:
            return sale_order.client_order_ref or ""
        return "/".join(
            [
                delivery_date.strftime("%y"),
                depot_number,
                sale_order.suite_name or "0000",
            ]
        )

    def _get_net_price(self):
        """Should be overridden to invove additonal product and consignment."""
        return self.sale_line_id.price_reduce_taxexcl

    def _get_crude_price(self):
        """Should be overridden to invove additonal product and consignment."""
        return self.sale_line_id.price_unit
