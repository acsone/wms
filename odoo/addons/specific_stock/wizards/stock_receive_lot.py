# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPackOperationLotAdd(models.TransientModel):
    _inherit = "stock.pack.operation.lot.add"

    @api.onchange("operation_id")
    def _onchange_operation_id(self):
        res = super(StockPackOperationLotAdd, self)._onchange_operation_id()
        if self.qty_backorder:
            op_dest_loc = self.operation_id.location_dest_id
            if op_dest_loc.usage == "internal" and not op_dest_loc.act_as_view:
                self.location_dest_id = op_dest_loc
            else:
                self.location_dest_id = False
        return res
