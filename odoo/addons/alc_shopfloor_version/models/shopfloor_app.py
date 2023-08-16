# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopfloor_base.models.shopfloor_app import (
    ShopfloorApp as ShopfloorAppBase,
)
from odoo.addons.shopfloor_base.utils import get_version


class ShopfloorApp(ShopfloorAppBase):
    def _compute_app_version(self):
        get_version("alc_all")
        self.update({"app_version": get_version("alc_all")})
