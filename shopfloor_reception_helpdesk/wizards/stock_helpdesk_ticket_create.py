# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockHelpdeskTicketCreate(models.TransientModel):
    _inherit = "stock.helpdesk.ticket.create"

    motive_id = fields.Many2one("helpdesk.ticket.motive")

    def _prepare_ticket_values(self) -> dict:
        res = super()._prepare_ticket_values()
        if self.env.context.get("from_shopfloor_reception"):
            res["is_shopfloor_created"] = True
            if self.motive_id:
                res[
                    "name"
                ] = f"[Shopfloor] {self.motive_id.name} - {self.stock_picking_id.name}"
            else:
                res["name"] = f"[Shopfloor] {self.stock_picking_id.name}"
        return res
