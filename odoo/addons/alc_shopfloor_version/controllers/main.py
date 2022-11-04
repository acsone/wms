# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopfloor_mobile_base.controllers.main import (
    ShopfloorMobileAppController,
)

from ..alc_version import _get_alc_version


class ShopfloorMobileAppControllerAlc(ShopfloorMobileAppController):
    def _get_app_version(self):
        return _get_alc_version()

    def _get_version(self, module_name, module_path=None):
        return self._get_app_version()
