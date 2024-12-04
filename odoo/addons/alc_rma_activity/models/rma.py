# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.rma.models.rma import Rma as RmaBase


class Rma(RmaBase):
    def _create_inventory_activity_reception(self):
        for rec in self:
            if rec.operation_id.create_inventory_activity_reception:
                summary = _("Inventory actions required after reception")
                self.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=None,
                    summary=summary,
                    user_id=rec.user_id.id if rec.user_id else rec.create_uid.id,
                )

    def _create_inventory_activity_delivery(self):
        for rec in self:
            if rec.operation_id.create_inventory_activity_delivery:
                summary = _("Inventory actions required after delivery")
                self.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=None,
                    summary=summary,
                    user_id=rec.user_id.id if rec.user_id else rec.create_uid.id,
                )
