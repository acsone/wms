# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api

from odoo.addons.stock.models import stock_picking


class StockPicking(stock_picking.Picking):
    @api.model
    def get_released_batch_candidates_domain(self):
        picking_ids = self.env["stock.picking.type"]._get_ids_visible_in_dashboard()
        wizard = self.env["make.picking.batch"].new(
            {
                "picking_type_ids": self.env["stock.picking.type"].browse(picking_ids),
                "maximum_number_of_preparation_lines": 500,
                "release_channel_required": True,
            }
        )
        return wizard._get_picking_domain_for_first(no_nbr_lines_limit=True)
