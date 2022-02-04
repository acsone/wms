# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component

from ..models.stock_pack_operation import NoReserveLocationError


class LocationContentTransfer(Component):
    _inherit = "shopfloor.location.content.transfer"

    def overstock_line(self, location_id, operation_id):
        """
        Change the location_dest to the reserve

        Transitions:
            * start_single: continue with the new operation to put products
            into reserve
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            operations = super(LocationContentTransfer, self)._find_operations(location)
            return self._response_for_start_single(
                operations.mapped("picking_id"),
                message=self.msg_store.record_not_found(),
            )
        try:
            operation._to_reserve()
            return self._response_for_start_single(operation.picking_id)
        except NoReserveLocationError:
            return self._response_for_start_single(
                operation.mapped("picking_id"),
                message=self.msg_store.no_reserve_location_found(
                    operation.location_dest_id
                ),
            )


class ShopfloorLocationContentTransferValidator(Component):
    """Validators for the Location Content Transfer endpoints"""

    _inherit = "shopfloor.location.content.transfer.validator"

    def overstock_line(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
        }


class ShopfloorLocationContentTransferValidatorResponse(Component):
    """Validators for the Location Content Transfer endpoints responses"""

    _inherit = "shopfloor.location.content.transfer.validator.response"

    def overstock_line(self):
        return self._response_schema(next_states={"start_single"})
