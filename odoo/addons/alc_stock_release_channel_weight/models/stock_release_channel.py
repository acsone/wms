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
        sql = """
            SELECT
                release_channel_id,
                sum(sm.weight) as weight
            FROM
                stock_move sm
                join stock_picking sp on sp.id = sm.picking_id
                join stock_picking_type spt on spt.id = sp.picking_type_id
            WHERE
                sp.release_channel_id in %s
                AND spt.code = 'outgoing'
                AND sp.state not in ('cancel', 'done', 'draft')
                AND sm.state not in ('cancel', 'done', 'draft')
            GROUP BY
                sp.release_channel_id;
        """
        self.env.cr.execute(sql, (tuple(self.ids),))
        total_weight_dict = dict(self.env.cr.fetchall())
        for rec in self:
            rec.total_weight = total_weight_dict.get(rec.id, 0.0)
