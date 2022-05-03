# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _notify_note(self):
        """ Send a mail to notify the sale service when a note is specified"""
        template = self.env.ref("alc_eshop_sale_cart_confirm.sale_order_notify_note")
        for record in self.filtered("note"):
            template.send_mail(record.id)
