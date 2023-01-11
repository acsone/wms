# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_picking_batch.models import stock_picking


class StockPicking(stock_picking.StockPicking):

    batch_state = fields.Selection(
        string="Picking batch state", related="batch_id.state", readonly=True
    )
