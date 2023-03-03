# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from datetime import datetime

from odoo import _

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    @contextmanager
    def _ensure_max_confirmation_delay_not_exceeded(self):
        yield
        now = datetime.now()
        for order in self:
            if not order.state == "sale":
                continue
            max_delay = order.partner_id.auto_confirm_max_delay
            if not max_delay:
                continue

            max_delay_in_seconds = max_delay * 60 * 60
            time_elapsed = now - order.create_date
            if time_elapsed.total_seconds() > max_delay_in_seconds:
                order.with_context(disable_cancel_warning=True).action_cancel()
                order.message_post(
                    body=_(
                        "Was automatically cancelled on creation because the "
                        "job took longer to execute than the customer allows."
                    )
                )

    def action_confirm_and_check_delay(self):
        with self._ensure_max_confirmation_delay_not_exceeded():
            self.filtered(lambda o: o.state != "sale").action_confirm()
