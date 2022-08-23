# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class LocationContentTransfer(Component):
    _inherit = "shopfloor.location.content.transfer"

    ############
    # SERVICES #
    ############

    def get_work(self):
        refill_arrange = self._refill_arrange_search()
        if refill_arrange:
            return super(LocationContentTransfer, self).scan_location(
                refill_arrange[0].location_id.barcode
            )

        refill_reassort = self._refill_reassort_search()
        if refill_reassort:
            return super(LocationContentTransfer, self).scan_location(
                refill_reassort[0].location_id.barcode
            )
        return super(LocationContentTransfer, self)._response_for_start(
            message=self.msg_store.location_content_transfer_no_work()
        )

    ##################
    # Helpers methods
    ##################
    def _refill_arrange_search(self):
        RefillArrange = self.env["report.stock.refill.arrange"]
        return RefillArrange.search(
            [
                ("reservation_id", "=", False),
                ("barcode_picking_type_id", "in", self.picking_types.ids),
            ],
            order="refill_priority_arrange desc",
        )

    def _refill_reassort_search(self):
        RefillReassort = self.env["report.stock.refill.reassort"]
        return RefillReassort.search(
            [
                ("reservation_id", "=", False),
                ("barcode_picking_type_id", "in", self.picking_types.ids),
            ],
            order="refill_priority_reassort desc",
        )


class ShopfloorLocationContentTransferValidator(Component):
    """Validators for the Location Content Transfer endpoints"""

    _inherit = "shopfloor.location.content.transfer.validator"

    def get_work(self):
        return {}


class ShopfloorLocationContentTransferValidatorResponse(Component):
    """Validators for the Location Content Transfer endpoints responses"""

    _inherit = "shopfloor.location.content.transfer.validator.response"

    def get_work(self):
        return self._response_schema(
            next_states={"start", "scan_destination_all", "start_single"}
        )
