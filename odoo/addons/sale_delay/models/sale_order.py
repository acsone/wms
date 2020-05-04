# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def is_delayed(self, from_time):
        """Check that a background operation does not take too long."""
        self.ensure_one()
        max_delay = self.partner_id.max_delay_for_sale_order_creation
        if not max_delay:
            return False
        max_delay_in_seconds = max_delay * 60 * 60
        time_elapsed = datetime.now() - from_time
        return time_elapsed.total_seconds() > max_delay_in_seconds
