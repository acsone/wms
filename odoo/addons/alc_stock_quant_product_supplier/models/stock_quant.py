# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.partner_manual_rank.models.res_partner import ResPartner
from odoo.addons.stock.models.stock_quant import StockQuant as StockQuantBase


class StockQuant(StockQuantBase):
    supplier_id = fields.Many2one[ResPartner](
        string="Vendor", readonly=True, related="product_id.supplier_id"
    )
