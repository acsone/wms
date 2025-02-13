# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    expiration_date = fields.Datetime(
        related="lot_id.expiration_date",
        store=True,
        index=True,
    )
