# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math

from odoo import api, models


class RoundInstance(models.Model):
    _inherit = 'round.instance'

    @api.multi
    def print_delivery_round(self):
        self.ensure_one()

        return self.env['report']\
            .get_action(self, 'delivery_rounds.delivery_round_report')

    @api.multi
    def get_time_leave_planned(self):
        self.ensure_one()

        if self.time_leave_planned <= 0:
            return ''

        pattern = '%02d:%02d'
        hour = math.floor(self.time_leave_planned)
        min = round((self.time_leave_planned % 1) * 60)
        if min == 60:
            min = 0
            hour += 1

        return pattern % (hour, min)
