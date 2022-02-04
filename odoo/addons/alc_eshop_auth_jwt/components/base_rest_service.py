# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import AbstractComponent


class BaseRestService(AbstractComponent):
    _inherit = "base.rest.service"

    def _get_openapi_paths(self):
        paths = super(BaseRestService, self)._get_openapi_paths()
        if self._collection == "shopinvader.backend":
            for _path, methods in paths.items():
                for _method, info in methods.items():
                    info["security"] = [{"jwt": []}]
        return paths
