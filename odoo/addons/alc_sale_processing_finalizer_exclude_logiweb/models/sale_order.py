# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.alc_sale_processing_finalizer.models.sale_order import (
    SaleOrder as SaleOrderBase,
)


class SaleOrder(SaleOrderBase):
    @api.model
    def _get_sales_bo_gt_3months_lines(self, sale_order=None):
        lines = super()._get_sales_bo_gt_3months_lines(sale_order=sale_order)
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
