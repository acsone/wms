# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class LocationContentTransfer(Component):

    _inherit = "shopfloor.location.content.transfer"

    def print_label(self, location_id, move_line_id, lot_id=None, printer_id=None):
        """Print label for current product."""
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        move_line = self.env["stock.move.line"].browse(move_line_id)
        if not move_line:
            return self._response_for_start(message=self.msg_store.record_not_found())

        printer_id = printer_id or self.env.user.printing_product_label_printer_id.id
        if lot_id:
            lot = self.env["stock.lot"].browse(lot_id)
            lot.print_lot_label(printer_id=printer_id)
        else:
            move_line.product_id.print_product_label(printer_id=printer_id)
        return self._response_for_start_single(
            move_line.picking_id, message=self.msg_store.confirm_print_label()
        )


class ShopfloorLocationContentTransferValidator(Component):
    """Validators for the Location Content Transfer endpoints."""

    _inherit = "shopfloor.location.content.transfer.validator"
    _usage = "location_content_transfer.validator"

    def print_label(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "move_line_id": {"coerce": to_int, "required": True, "type": "integer"},
            "lot_id": {
                "coerce": to_int,
                "required": False,
                "nullable": True,
                "type": "integer",
            },
        }


class ShopfloorLocationContentTransferValidatorResponse(Component):
    """Validators for the Location Content Transfer endpoints responses."""

    _inherit = "shopfloor.location.content.transfer.validator.response"
    _usage = "location_content_transfer.validator.response"

    def print_label(self):
        return self._response_schema(next_states={"start", "start_single"})
