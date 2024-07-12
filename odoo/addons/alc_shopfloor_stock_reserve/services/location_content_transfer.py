# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.shopfloor.services.location_content_transfer import (
    LocationContentTransfer as LocationContentTransferBase,
    ShopfloorLocationContentTransferValidator as LocationContentTransferValidator,
    ShopfloorLocationContentTransferValidatorResponse as LocationContentTransferValidatorResponse,
)

from ..models.stock_move_line import NoReserveLocationError


class LocationContentTransfer(LocationContentTransferBase):
    def overstock_line(self, location_id, move_line_id):
        """
        Change the location_dest to the reserve.

        Transitions:
            * start_single: continue with the new operation to put products
            into reserve
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        move_line = self.env["stock.move.line"].browse(move_line_id)
        if not move_line.exists():
            move_lines = self.search_move_line.search_move_lines(
                locations=location, match_user=True
            )
            return self._response_for_start_single(
                move_lines.picking_id,
                message=self.msg_store.record_not_found(),
            )
        try:
            move_line._to_reserve()
            return self._response_for_start_single(move_line.picking_id)
        except NoReserveLocationError:
            return self._response_for_start_single(
                move_line.picking_id,
                message=self.msg_store.no_reserve_location_found(
                    move_line.location_dest_id
                ),
            )


class ShopfloorLocationContentTransferValidator(LocationContentTransferValidator):
    """Validators for the Location Content Transfer endpoints."""

    def overstock_line(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "move_line_id": {"coerce": to_int, "required": True, "type": "integer"},
        }


class ShopfloorLocationContentTransferValidatorResponse(
    LocationContentTransferValidatorResponse
):
    """Validators for the Location Content Transfer endpoints responses."""

    def overstock_line(self):
        return self._response_schema(next_states={"start_single"})
