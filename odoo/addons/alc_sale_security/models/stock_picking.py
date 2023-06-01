# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.delivery.models.stock_picking import StockPicking as StockPickingBase


class StockPicking(StockPickingBase):
    def _add_delivery_cost_to_so(self):
        """Do not force 'Inventory User' to have create/write rights on sales."""
        return super(StockPicking, self.sudo())._add_delivery_cost_to_so()
