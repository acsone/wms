# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):
    total_weight = fields.Float(compute="_compute_total_weight")
    weight_uom_name = fields.Char(
        string="Weight unit of measure label", compute="_compute_weight_uom_name"
    )

    def _compute_weight_uom_name(self):
        self.weight_uom_name = self.env[
            "product.template"
        ]._get_weight_uom_name_from_ir_config_parameter()

    def _compute_total_weight(self):
        picking_model = self.env["stock.picking"]
        common_domain = [
            ("picking_type_code", "=", "outgoing"),
            ("state", "not in", ("done", "cancel")),
        ]
        for rec in self:
            domain = common_domain + [("release_channel_id", "=", rec.id)]
            pickings = picking_model.search(domain)
            if not pickings:
                rec.total_weight = 0
            else:
                rec.total_weight = sum(pickings.mapped("total_weight"))
