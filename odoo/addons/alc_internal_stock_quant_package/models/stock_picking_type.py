# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    empty_internal_package_on_transfer = fields.Boolean(
        help="If set internal packages are emptied after the transfer or "
        "when products are put in pack.",
        default=True,
    )
    stock_internal_package_config_line_ids = fields.One2many(
        comodel_name="stock.internal.package.config.line",
        inverse_name="stock_picking_type_id",
    )

    @api.model
    @tools.ormcache("picking_type_id", "carrier_id")
    def _empty_internal_package_on_transfer(self, picking_type_id, carrier_id):
        picking_type = self.browse(picking_type_id)
        result = picking_type.empty_internal_package_on_transfer
        filter_carrier = lambda cl: cl.delivery_carrier_id.id == carrier_id
        lines = picking_type.stock_internal_package_config_line_ids
        carrier_line = lines.filtered(filter_carrier)
        if carrier_line:
            result = carrier_line.empty
        return result
