# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    def bind_all_category(self, domain=None):
        domain = domain or []
        domain.append(("is_web", "=", True))
        return super(ShopinvaderBackend, self).bind_all_category(domain=domain)
