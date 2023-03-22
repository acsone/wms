# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_rest.controllers import main


class InvaderControllerJWT(main.RestController):

    _root_path = "/shopinvader_jwt/v2/"
    _collection_name = "shopinvader.api.v2"
    _default_auth = "jwt_shopinvader"
    _default_save_session = False
    _default_cors = "*"
    _component_context_provider = "shopinvader_auth_jwt_context_provider"


class InvaderControllerAPIKEY(main.RestController):

    _root_path = "/shopinvader/v2/"
    _collection_name = "shopinvader.api.v2"
    _default_auth = "api_key"
    _default_save_session = False
    _default_cors = "*"
    _component_context_provider = "auth_api_key_component_context_provider"
