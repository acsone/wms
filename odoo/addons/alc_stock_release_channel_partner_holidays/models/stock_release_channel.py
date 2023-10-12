# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as ChannelBase,
)

_logger = logging.getLogger(__name__)


class StockReleaseChannel(ChannelBase):

    _inherit = "stock.release.channel"

    def _assign_release_channel_additional_filter(self, pickings):
        pickings = super()._assign_release_channel_additional_filter(pickings)
        not_holidays_pickings = pickings.filtered(
            lambda pick: pick.partner_id.is_shipping_date_allowed(self.process_end_date)
        )
        to_log_pickings = self.env["stock.picking"].browse(
            set(set(pickings.ids) - set(not_holidays_pickings.ids))
        )
        if to_log_pickings:
            # TODO: Put these into activities for stock manager
            _logger.info(
                "RELEASE CHANNEL: Some pickings have their partner in holidays: %(pickings_name)s",
                {"pickings_name": ",".join([to_log_pickings.name])},
            )
        return not_holidays_pickings
