# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

_logger = logging.getLogger(__name__)


class StockReleaseChannel(StockReleaseChannelBase):
    @api.model
    def assign_release_channel(self, picking):
        picking.ensure_one()
        if (
            not picking.ignore_release_channel_block
            and picking.delivery_requires_other_lines
        ):
            message_template = (
                "Transfer %(picking_name)s could not be assigned to a channel because "
                "it's blocked. It requires either a new order to be unblocked or a "
                "manual action from the user."
            )
            _logger.warning(message_template, {"picking_name": picking.name})
            return _(message_template, picking_name=picking.name)
        return super().assign_release_channel(picking)
