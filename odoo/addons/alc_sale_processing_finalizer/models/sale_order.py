# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields

from odoo.addons.alc_sale_consignment.models.sale_order import SaleOrder as Order


class SaleOrder(Order):

    auto_finalize_processing = fields.Boolean(
        default=True, help="Set to true to automatically purge SO after 3 months"
    )

    @api.model
    def _get_sales_bo_gt_3months_lines_domain(self, sale_order=None):
        domain = [
            ("product_qty_remains_to_deliver", ">", 0),
            ("product_type", "in", ["consu", "product"]),
            ("is_consignment", "=", False),
            (
                "date_order",
                "<",
                (datetime.datetime.today() - relativedelta(months=3)).date(),
            ),
        ]
        if sale_order:
            domain.append(("order_id", "=", sale_order.id))
        return domain

    @api.model
    def cancel_sales_bo_gt_3months(self):
        lines = self._get_sales_bo_gt_3months_lines()
        self._cancel_sales_bo_gt_3months_send_mail(lines)
        self._cancel_sales_bo_gt_3months(lines)

    @api.model
    def _cancel_sales_bo_gt_3months(self, lines):
        wizard = self.env["sale.order.line.cancel"].new()
        for line in lines:
            moves = line.move_ids
            remaining_moves = moves.filtered(
                lambda m: m.state not in ("cancel", "done")
            )
            if not remaining_moves:
                line.write(
                    {"product_qty_canceled": line.product_qty_remains_to_deliver}
                )
            wiz = wizard.with_context(active_id=line.id, active_model=line._name)
            wiz.cancel_remaining_qty()

    @api.model
    def _cancel_sales_bo_gt_3months_send_mail(self, lines):
        send_processing_finalizer_email = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_sale_processing_finalizer.send_email", False)
        )
        if not send_processing_finalizer_email:
            return
        mail_template = self.env.ref("alc_sale_processing_finalizer.mail_template_30")
        mail_template.model = self._name
        for canceled_order in lines.order_id:
            mail_template.send_mail(canceled_order.id, force_send=True)

    @api.model
    def _get_sales_bo_gt_3months_lines(self, sale_order=None):
        lines = self.env["sale.order.line"].search(
            self._get_sales_bo_gt_3months_lines_domain(sale_order=sale_order)
        )
        return lines.filtered(
            lambda line: not line.order_id.carrier_id.is_long_term_delivery
            and line.state not in ("draft", "sent")
            and line._is_cancel_sales_bo_gt_3months_allowed()
        )
