# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


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
