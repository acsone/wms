# -*- coding: utf-8 -*-
# Copyright 2016-2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019-2020 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    # In : stock_procurement_customer
    # def _get_new_picking_values(self):
    #     """ Prepares a new picking for this move as it could not be assigned to
    #     another picking.
    #     Add the customer from the procurement group.
    #     """
    #     self.ensure_one()
    #     res = super(StockMove, self)._get_new_picking_values()
    #     res["customer_id"] = self.group_id.customer_id.id
    #     return res

    
    # TODO: Check if still necessary
    # Note: Odoo allows to cancel a printed picking. Maybe put the restriction in
    # a further module
    # @api.multi
    # def action_cancel(self):
    #     """ Prevent to cancel a move from a printed picking and recompute pack
    #     operations """
    #     _logger.debug("Canceling moves %s", self.ids)
    #     res = super(StockMove, self).action_cancel()
    #     if not self.env.context.get("no_recompute_pack"):
    #         pickings = self.mapped("picking_id").filtered(
    #             lambda picking: picking.state != "cancel"
    #         )
    #         products = self.mapped("product_id")
    #         moves = pickings.mapped("move_lines").filtered(
    #             lambda move: move.state == "confirmed" and move.product_id in products
    #         )
    #         if moves:
    #             # action_assign requires to clean existing pack operation
    #             moves.mapped("linked_move_operation_ids.operation_id").unlink()
    #             _logger.debug("Re-check availability for moves %s", moves.ids)
    #             moves.action_assign(no_prepare=True)
    #         # recompute pack op
    #         _logger.debug("Recompute pack operations")
    #         pickings.do_prepare_partial()
    #         # Recompute the weight for each picking
    #         self.exists().mapped("picking_id")._cal_weight()
    #     return res
