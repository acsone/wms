# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import traceback

from odoo import _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase

_logger = logging.getLogger("restrict-zero-quantity-error")


class StockMoveLine(StockMoveLineBase):
    def _check_alc_stock_move_line_restrict_quantity(self, vals) -> None:
        """
        This method checks if the feature to log error when updating the.

        reserved_uom_qty field is enabled and updating value is O and
        original value was not 0.
        """
        self.ensure_one()
        raise_exception = self.company_id.restrict_move_line_quantity
        invalid_value = bool(
            self.state != "done"
            and "reserved_uom_qty" in vals
            and vals.get("reserved_uom_qty") <= 0.0
            and not float_compare(
                self._origin.reserved_uom_qty,
                0.0,
                precision_rounding=self.product_id.uom_id.rounding,
            )
            <= 0
        )
        if invalid_value:
            # Log the error
            message = _(
                "The demand quantity should not be set to 0 or negative in the picking %(picking_name)s for product %(product_name)s",
                picking_name=self.picking_id.name,
                product_name=self.product_id.name,
            )
            # pylint: disable=logging-not-lazy
            _logger.error(message + "\n".join(traceback.format_stack()))
            if raise_exception:
                raise UserError(message)

    def write(self, vals):
        for rec in self:
            rec._check_alc_stock_move_line_restrict_quantity(vals)
        return super().write(vals)
