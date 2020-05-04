# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class RoundInstance(models.Model):
    _inherit = "round.instance"

    @api.multi
    def button_done(self):
        self.ensure_one()
        res = super(RoundInstance, self).button_done()
        return res
