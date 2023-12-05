# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_sale_processing_finalizer.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    def _filter_sale_order_lines_to_cancel(self, lines):
        lines = super()._filter_sale_order_lines_to_cancel(lines)
        logiweb_sa = self.env.ref(
            "alc_logiweb.logiweb_partner",
            raise_if_not_found=False,
        )
        logiweb_be = self.env.ref(
            "alc_logiweb.logiweb_be_partner",
            raise_if_not_found=False,
        )
        return lines.filtered(
            lambda line: line.order_id.partner_invoice_id
            not in (logiweb_be, logiweb_sa)
        )
