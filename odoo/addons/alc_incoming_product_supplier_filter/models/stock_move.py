# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.stock.models import stock_move


class StockMove(stock_move.StockMove):

    supplier_id = fields.Many2one[Partner](
        string="Vendor",
        readonly=True,
        related="product_tmpl_id.supplier_id",
    )
