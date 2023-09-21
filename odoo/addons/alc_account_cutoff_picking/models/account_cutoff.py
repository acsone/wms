# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account_cutoff_picking.models.account_cutoff import (
    AccountCutoff as AccountCutoffBase,
)


class AccountCutoff(AccountCutoffBase):
    def _get_sale_lines(self):
        sale_order_line_model = self.env["sale.order.line"]
        with sale_order_line_model._auto_join(["order_id"]):
            lines = self.env["sale.order.line"].search(
                [("qty_to_invoice", "!=", 0), ("order_id.state", "!=", "done")]
            )
        return lines

    def _get_purchase_lines(self):
        purchase_order_line_model = self.env["purchase.order.line"]
        with purchase_order_line_model._auto_join(["order_id"]):
            lines = self.env["purchase.order.line"].search(
                [("qty_to_invoice", "!=", 0), ("order_id.state", "!=", "done")]
            )
        return lines
