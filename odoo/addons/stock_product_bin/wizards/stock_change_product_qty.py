# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain Van Hoof <svh@sylvainvh.be>
#    Copyright (C) 2016
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models


class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.model
    def _get_default_location_id(self):
        if self.env.context.get(
            "active_model"
        ) != "product.template" or not self.env.context.get("active_id"):
            return

        product_tmpl_id = self.env.context["active_id"]
        stock_bins = self.env["product.stock.bin"].search(
            [("product_id", "=", product_tmpl_id)], limit=1
        )

        if stock_bins:
            return stock_bins.bin_location_id.id

    location_id = fields.Many2one(default=_get_default_location_id)
