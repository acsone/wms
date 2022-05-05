# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        # Normally, force_quotation_send is called by the super based on a context key
        # 'send_email'. Since we want to only send the email in some cases, that would
        # mean to split the super call with a costly context change.
        # This will certainly need to be changed at migration.
        res = super(SaleOrder, self).action_confirm()
        if self.env["sale.config.settings"].get_send_confirmation_email_internal():
            internal_channels = self._get_sale_channels_internal()
            for order in self.filtered(lambda so: so.sale_channel in internal_channels):
                order.force_quotation_send()
        return res
