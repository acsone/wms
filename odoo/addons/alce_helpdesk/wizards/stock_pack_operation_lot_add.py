# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, api, fields
from odoo.tools import float_compare

from odoo.addons.alc_stock_receive_lot.wizards.stock_pack_operation_lot_add import (
    StockPackOperationLotAdd as PackOperationLotAdd,
)

from ..models.helpdesk_ticket import HelpdeskTicketReason


class StockPackOperationLotAdd(PackOperationLotAdd):

    helpdesk_ticket_reason_id = fields.Many2one[HelpdeskTicketReason](
        domain=[("visible_reception_wizard", "=", 1)],
        string="Reason",
    )
    helpdesk_ticket_description = fields.Char(string="Description")

    @api.onchange("helpdesk_ticket_reason_id")
    def _onchange_helpdesk_ticket_reason(self):
        if self.helpdesk_ticket_reason_id:
            if self.helpdesk_ticket_reason_id.location_dest_id:
                self.location_dest_id = self.helpdesk_ticket_reason_id.location_dest_id

    def _create_helpdesk_ticket(self):
        """Create helpdesk ticket if required."""
        self.ensure_one()
        if self.helpdesk_ticket_reason_id:
            ticket = {
                "helpdesk_ticket_reason_id": self.helpdesk_ticket_reason_id.id,
                "name": self.helpdesk_ticket_description,
                "partner_id": self.partner_id.id,
                "stock_picking_id": self.picking_id.id,
                "product_id": self.move_line_id.product_id.id,
                "team_id": self.env.ref("alce_helpdesk.supplier_team").id,
            }
            if self.move_line_id.picking_id.purchase_id:
                ticket["purchase_order_id"] = self.picking_id.purchase_id.id
            self.env["helpdesk.ticket"].create(ticket)
        self.helpdesk_ticket_reason_id = False
        self.helpdesk_ticket_description = False

    def _add(self):
        res = super()._add()
        operation = self.move_line_id
        self._create_helpdesk_ticket()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if (
            float_compare(
                operation.qty_done,
                operation.reserved_uom_qty,
                precision_digits=precision,
            )
            > 0
        ):
            self.helpdesk_ticket_reason_id = self.env.ref(
                "alce_helpdesk.higher_quantity"
            )
            self.helpdesk_ticket_description = _(
                "Received more than expected qties for product '%(name)s'. "
                "(Expected: %(qty)d, Received %(qty_done)d)",
                name=operation.product_id.display_name,
                qty=operation.reserved_uom_qty,
                qty_done=operation.qty_done,
            )
            self._create_helpdesk_ticket()
        return res
