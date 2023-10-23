# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def action_validate_and_print_delivery(self):
        if self.filtered(
            lambda p: p.state != "assigned" or p.picking_type_code != "outgoing"
        ):
            raise UserError(_("This action is allowed only for ready deliveries"))
        self.action_set_quantities_to_reservation()
        self._action_done()
        return self.env.ref("stock.action_report_delivery").report_action(self)
