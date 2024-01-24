# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    def action_cancel(self):
        for sale_order in self:
            if sale_order.picking_ids.filtered(
                lambda picking: picking.printed or picking.state == "done"
            ):
                raise UserError(
                    _("You cannot cancel sale order {}, it's already prepared").format(
                        sale_order.name
                    )
                )
        return super().action_cancel()
