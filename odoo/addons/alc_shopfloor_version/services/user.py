# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component

from ..alc_version import _get_alc_version


class ShopfloorUser(Component):
    _inherit = "shopfloor.user"

    def shopfloor_version(self):
        return self._response(data={"version": _get_alc_version()})
