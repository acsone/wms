# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner

from .partner_working_schedule import PartnerManagedDays


class ResPartner(Partner):

    working_schedules_ids = fields.One2many[PartnerManagedDays](
        inverse_name="partner_id",
        string="Partner Holidays",
    )

    def is_shipping_date_allowed(self, day: fields.Date) -> bool:
        """
        This is the method to call on a partner to check if it's not closed.

        :param day: The day to check
        :type day: date
        :return: _description_
        :rtype: bool
        """
        if not self:
            return True
        self.ensure_one()
        return not bool(
            self.working_schedules_ids.filtered(
                lambda l: l.start_date <= day and (l.end_date >= day or not l.end_date)
            )
        )
