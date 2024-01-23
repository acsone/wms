# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models

from odoo.addons.stock.models.stock_picking import PickingType

from .stock_release_channel import StockReleaseChannel


class StockReleaseChannelPickAllowedLog(models.Model):

    _name = "stock.release.channel.pick.allowed.log"
    _description = "Stock Release Channel Pick Allowed Log"
    _order = "create_date desc, release_channel_id desc, picking_type_id desc"

    release_channel_id = fields.Many2one[StockReleaseChannel](
        index=True,
        ondelete="cascade",
    )
    picking_type_id = fields.Many2one[PickingType](
        index=True,
        ondelete="cascade",
    )

    allowed = fields.Boolean()

    @api.model
    def cron_garbage_collector(self, nb_days=14):
        """Delete logs older than nb_days."""
        self.search(
            [("create_date", "<", datetime.now() - timedelta(days=nb_days))]
        ).unlink()
