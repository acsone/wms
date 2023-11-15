# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models import sale_order


class SaleOrder(sale_order.SaleOrder):

    import_warning_msg = fields.Text()

    def _notify_note(self):
        """Send a mail to notify the sale service when a note is specified."""
        template = self.env.ref("alc_eshop_api_cart.sale_order_notify_note")
        for record in self.filtered("note"):
            template.send_mail(record.id, force_send=True)
