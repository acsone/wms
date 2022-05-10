# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ShopinvaderBackend(models.Model):
    _inherit = ["shopinvader.backend"]

    @property
    def _server_env_fields(self):
        _env_fields = [
            "jwt_aud",
        ]
        res = super(ShopinvaderBackend, self)._server_env_fields
        res.update({k: {} for k in _env_fields})
        return res

    @api.model
    def _get_jwt_aud_domain(self, aud_list):
        res = super(ShopinvaderBackend, self)._get_jwt_aud_domain(aud_list)
        return [element for element in res if element[0] != "jwt_aud"]

    @api.model
    def _get_jwt_aud_from_domain(self, domain, aud_list):
        res = super(ShopinvaderBackend, self)._get_jwt_aud_from_domain(domain)
        return res.filtered(lambda b: b.jwt_aud in aud_list)
