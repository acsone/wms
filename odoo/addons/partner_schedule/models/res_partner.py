# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    working_schedules_ids = fields.One2many(
        "partner.scheduled.week",
        "partner_id",
        string="Partner Schedule",
        ondelete="cascade",
    )

    def is_shipping_date_allowed(self, day):

        if not self:
            return True
        self.ensure_one()
        return not bool(
            self.working_schedules_ids.filtered(
                lambda l: l.start_date <= day and (l.end_date >= day or not l.end_date)
            )
        )
