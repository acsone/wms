# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _gls_prepare_address(self):
        self.ensure_one()
        address_payload = super(ResPartner, self)._gls_prepare_address()
        address_payload["Name2"] = self.suite if self.suite else ""
        return address_payload
