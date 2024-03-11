# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import traceback

from odoo import api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase

_logger = logging.getLogger("restrict-zero-quantity-error")


class StockMoveLine(StockMoveLineBase):
    @api.model
    def _check_alc_stock_move_line_reserved_uom_qty(self, vals):
        return bool("reserved_uom_qty" in vals and vals.get("reserved_uom_qty") <= 0.0)

    def _check_alc_stock_move_line_restrict_quantity(self, vals) -> None:
        """
        This method checks if the feature to log error when updating the.

        reserved_uom_qty field is enabled and updating value is O and
        original value was not 0.
        """
        self.ensure_one()
        raise_exception = self.company_id.restrict_move_line_quantity
        no_restriction_quantity_ids = self.env.context.get(
            "no_restriction_quantity_ids", []
        )
        invalid_value = bool(
            self.id not in no_restriction_quantity_ids
            and self.state != "done"
            and not float_compare(
                self._origin.reserved_uom_qty,
                0.0,
                precision_rounding=self.product_id.uom_id.rounding,
            )
            <= 0
        )
        if invalid_value:
            stack = traceback.format_stack()
            message_template = "The demand quantity should not be set to 0 or negative in the picking %s for product %s\n\n%s"
            # Log the error
            _logger.error(
                message_template, self.picking_id.name, self.product_id.name, stack
            )
            if raise_exception:
                raise UserError(
                    message_template
                    % (self.picking_id.name, self.product_id.name, stack)
                )

    def _action_done(self):
        new_self = self.with_context(no_restriction_quantity_ids=self.ids)
        return super(StockMoveLine, new_self)._action_done()

    def write(self, vals):
        # Check field modification first
        if self._check_alc_stock_move_line_reserved_uom_qty(vals):
            for rec in self:
                rec._check_alc_stock_move_line_restrict_quantity(vals)
        return super().write(vals)

    # Functions that will be allowed
    def _create_loss_picking(self, group_key):
        # TODO: Check if there is a better way to do the loss operation
        # without writing to reserved_uom_qty
        new_self = self.with_context(no_restriction_quantity_ids=self.ids)
        return super(StockMoveLine, new_self)._create_loss_picking(group_key=group_key)

    def _split_for_loss(self) -> dict:
        # TODO: Check if there is a better way to do the loss operation
        # without writing to reserved_uom_qty
        new_self = self.with_context(no_restriction_quantity_ids=self.ids)
        return super(StockMoveLine, new_self)._split_for_loss()
