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
    def _get_sales_bo_gt_3months_lines_domain(self):
        return [
            ("product_qty_remains_to_deliver", ">", 0),
            ("product_type", "in", ["consu", "product"]),
            ("is_consignment", "=", False),
            (
                "date_order",
                "<",
                (datetime.datetime.today() - relativedelta(months=3)).date(),
            ),
        ]

    def _get_sales_bo_gt_3months_lines(self):
        self.ensure_one()
        return self.order_line.filtered_domain(
            self._get_sales_bo_gt_3months_lines_domain()
        ).filtered(lambda line: line._is_cancel_sales_bo_gt_3months_allowed())

    @api.model
    def cancel_sales_bo_gt_3months(self):
        wizard = self.env["sale.order.line.cancel"].new()
        mail_template = self.env.ref("alc_sale_processing_finalizer.mail_template_30")
        lines = self.env["sale.order.line"].search(
            self._get_sales_bo_gt_3months_lines_domain()
        )
        canceled_orders = self.env["sale.order"]
        lines = self._filter_sale_order_lines_to_cancel(lines)
        for line in lines:
            moves = line.move_ids
            remaining_moves = moves.filtered(
                lambda m: m.state not in ("cancel", "done")
            )
            if not remaining_moves:
                line.write(
                    {"product_qty_canceled": line.product_qty_remains_to_deliver}
                )
            if line._is_cancel_sales_bo_gt_3months_allowed():
                canceled_orders |= line.order_id
                wiz = wizard.with_context(active_id=line.id, active_model=line._name)
                wiz.cancel_remaining_qty()

        send_processing_finalizer_email = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_sale_processing_finalizer.send_email", False)
        )
        if not send_processing_finalizer_email:
            return

        mail_template.model = self._name
        for canceled_order in canceled_orders:
            mail_template.send_mail(canceled_order.id, force_send=True)

    def _filter_sale_order_lines_to_cancel(self, lines):
        return lines.filtered(
            lambda line: not line.order_id.carrier_id.is_long_term_delivery
            and line.state not in ("draft", "sent")  # filter quotations
        )
