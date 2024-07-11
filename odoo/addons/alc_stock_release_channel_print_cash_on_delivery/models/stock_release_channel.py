# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock_release_channel_shipment_advice_deliver.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):
    is_action_print_cash_invoices_allowed = fields.Boolean(
        compute="_compute_is_action_print_cash_invoices_allowed"
    )

    @api.depends("state")
    def _compute_is_action_print_cash_invoices_allowed(self):
        for rec in self:
            rec.is_action_print_cash_invoices_allowed = rec.state == "delivered"

    def _check_is_action_print_cash_invoices_allowed(self):
        for rec in self:
            if not rec.is_action_print_cash_invoices_allowed:
                raise UserError(
                    _(
                        "Action 'Print INV' is not allowed for channel %(name)s.",
                        name=rec.name,
                    )
                )

    def action_print_cash_invoices(self):
        self._check_is_action_print_cash_invoices_allowed()
        done_shipment_advices = self.in_process_shipment_advice_ids.filtered(
            lambda s: s.state == "done"
        )
        cash_invoices = done_shipment_advices.mapped("loaded_picking_ids").mapped(
            "cash_on_delivery_invoice_ids"
        )
        if cash_invoices:
            return self.env.ref(
                "account.account_invoices_without_payment"
            ).report_action(cash_invoices)
        raise UserError(_("No cash on delivery invoice to print"))
