# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.rma.models.rma import Rma as RmaBase


class Rma(RmaBase):
    def _create_inventory_activity(self):
        for rec in self:
            if rec.operation_id.create_inventory_activity:
                summary = _("Inventory actions required")
                self.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=None,
                    summary=summary,
                    user_id=rec.user_id.id if rec.user_id else rec.create_uid.id,
                )

    def action_confirm(self):
        res = super().action_confirm()
        self._create_inventory_activity()
        return res
