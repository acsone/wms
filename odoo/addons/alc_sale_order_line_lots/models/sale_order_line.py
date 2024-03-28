# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderlineBase
from odoo.addons.stock.models.stock_lot import StockLot as StockLotBase


class SaleOrderLine(SaleOrderlineBase):
    lot_ids = fields.Many2many[StockLotBase](
        compute="_compute_lot_ids",
        string="Lots/Serial Numbers",
    )

    older_lot_expiration_date = fields.Datetime(
        string="Expiration date",
        related="product_id.older_lot_id.expiration_date",
        readonly=True,
    )

    @api.depends("product_id")
    def _compute_lot_ids(self):
        lots = (
            self.env["stock.lot"]
            .search([("product_id", "in", self.mapped("product_id").ids)])
            .filtered(lambda p: p.qty_available > 0)
        )
        lot_ids_by_product_id = defaultdict(list)
        for lot in lots:
            lot_ids_by_product_id[lot.product_id.id].append(lot.id)
        for line in self:
            lot_ids = lot_ids_by_product_id.get(line.product_id.id)
            if lot_ids:
                line.lot_ids = [fields.Command.set(lot_ids)]
            else:
                line.lot_ids = False

    def action_view_lots(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "alc_sale_order_line_lots.action_sale_line_lots"
        )
        action["domain"] = [("id", "in", self.lot_ids.ids)]
        return action
