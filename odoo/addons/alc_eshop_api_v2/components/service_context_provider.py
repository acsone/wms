# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ShopinvaderAuthJwtServiceContextProvider(Component):
    _inherit = "auth_jwt.shopinvader.service.context.provider"
    _name = "auth_jwt.shopinvader.api.v2.service.context.provider"
    _collection = "shopinvader.api.v2"


class ShopinvaderAuthApiKeyServiceContextProvider(Component):
    _inherit = "auth_api_key.shopinvader.service.context.provider"
    _name = "auth_api_key.shopinvader.api.v2.service.context.provider"
    _collection = "shopinvader.api.v2"
