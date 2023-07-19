# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase

_logger = logging.getLogger(__name__)


class StockMove(StockMoveBase):

    # The field is computed into the SQL query in the method
    # _compute_waiting_for_reception of the model stock.picking
    count_partners_for_reception = fields.Integer(
        "Nbr partner linked to this product in reception",
    )
