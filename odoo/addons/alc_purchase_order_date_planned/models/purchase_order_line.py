# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields

from odoo.addons.purchase.models.purchase import (
    PurchaseOrderLine as PurchaseOrderLineBase,
)


class PurchaseOrderLine(PurchaseOrderLineBase):

    date_planned = fields.Datetime(readonly=False, states=False)

    @api.model
    def _get_date_planned(self, seller, po=False):
        """
        Inherit the method "_get_date_planned" in the module purchase.

        The original method has the decorator "api.model" but
        it shouldn't be as self is used as record not a model.
        """
        date_planned = False
        if not po:
            po = self.order_id
        if po.date_planned:
            date_planned = po.date_planned
        if not date_planned:
            date_order = po.date_order
            date_planned = self._get_next_scheduled_date(seller, date_order)
        if not date_planned:
            date_planned = super()._get_date_planned(seller, po=po)
        return date_planned

    def _get_next_scheduled_date(self, seller, date_order=None):
        """
        Return the scheduled date.

        :return: datetime - the scheduled date
        """
        # By default, take the delivery lead time on the supplier info
        if seller:
            lead_time = seller.delay
        # If there is no supplier info for this product, we take
        # the delivery lead time on the supplier
        elif len(self) == 1:
            lead_time = self.order_id.partner_id.delivery_lead_time
        else:
            lead_time = 0

        if date_order:
            date_planned = date_order
        else:
            date_planned = fields.Date.context_today(self)

        holiday_model = self.env["hr.holidays.public.line"]
        index = 0
        while index < lead_time:
            date_planned += timedelta(days=1)
            holiday = holiday_model.search([("date", "=", date_planned)])
            if holiday:
                continue
            # Check if the date planned is Saturday or Sunday
            if date_planned.isoweekday() in [6, 7]:
                continue
            index += 1
        return date_planned
