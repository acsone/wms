# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockLocationWizardChecksum(models.TransientModel):
    _name = "stock.location.wizard.checksum"

    @api.multi
    def generate(self):
        self.env["stock.location"].browse(
            self.env.context["active_ids"]
        ).generate_checksum()

    @api.multi
    def check(self):
        self.env["stock.location"].browse(
            self.env.context["active_ids"]
        ).check_checksum_valid()
