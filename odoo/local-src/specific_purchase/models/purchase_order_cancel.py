# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class PurchaseOrderCancel(models.TransientModel):
    _inherit = 'purchase.order.cancel'

    def confirm_cancel(self):
        result = super(PurchaseOrderCancel, self).confirm_cancel()

        purchase_id = self.env.context['active_ids']
        purchase = self.env['purchase.order'].browse(purchase_id)

        template = self.env.ref(
            'specific_purchase.cancel_purchase_order'
        )
        template.send_mail(purchase.id, force_send=True, raise_exception=True)

        return result
