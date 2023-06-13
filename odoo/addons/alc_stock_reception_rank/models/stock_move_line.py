# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase

_logger = logging.getLogger(__name__)


class StockMoveLine(StockMoveLineBase):

    # The field is computed into the SQL query in the method
    # _compute_waiting_for_reception of the model stock.picking
    count_partners_waiting_for_reception = fields.Integer(
        "Nbr partner waiting for this product",
        help="Quantity of deliveries part of a release_channel waiting for "
        "availability of this product. This field is only filled for "
        "receptions.",
    )
