# Copyright 2024 ACSONE AS/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):

    _rec_names_search = ["product_id", "product_id.vendor_product_code"]
