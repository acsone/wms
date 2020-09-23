# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

import dateutil

from odoo import api, fields, models
from odoo.tools import config


class SaleOrder(models.Model):

    _inherit = "sale.order"

    auto_finalize_processing = fields.Boolean(
        default=True, help="Set to true to automatically purge SO after 3 months"
    )

    @api.model
    def cancel_sales_bo_gt_3months(self):
        wizard = self.env["cancel.remaining.wizard"].new()
        mail_template = self.env.ref("alc_sale_processing_finalizer.mail_template_30")

        lines = self.env["sale.order.line"].search(
            [
                ("product_qty_remains_to_deliver", ">", 0),
                ("product_type", "in", ["consu", "product"]),
                ("is_consignment", "=", False),
                (
                    "date_order",
                    "<",
                    (
                        datetime.datetime.today()
                        - dateutil.relativedelta.relativedelta(months=3)
                    ).strftime("%Y-%m-%d"),
                ),
            ]
        )

        canceled_orders = self.env["sale.order"]

        lines = lines.filtered(
            lambda line: line.order_id.carrier_id
            != self.env.ref("alc_sale_processing_finalizer.deliver_carrier_long_term")
        )

        for line in lines:

            moves = line.procurement_ids.mapped("move_ids")

            remaining_moves = moves.filtered(
                lambda m: m.state not in ("cancel", "done")
            )
            if not remaining_moves:
                line.write(
                    {"product_qty_canceled": line.product_qty_remains_to_deliver}
                )
                continue
            if True in remaining_moves.mapped("picking_id.printed"):
                continue

            internal_moves = remaining_moves.mapped("move_orig_ids")
            if "done" in internal_moves.mapped("state"):
                continue
            if True in internal_moves.mapped("picking_id.printed"):
                continue

            if line.order_id.auto_finalize_processing:
                canceled_orders |= line.order_id
                wiz = wizard.with_context(active_id=line.id)
                wiz.cancel_remaining_qty()

        if config["test_enable"]:
            # Do not send mails during tests
            return
        for canceled_order in canceled_orders:
            mail_template.send_mail(canceled_order.id)
