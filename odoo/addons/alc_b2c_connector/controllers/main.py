# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main
from odoo.http import request

from ..services.base_b2c_service import CHRONOVET_COLLECTION


class RestController(main.RestController):
    _root_path = "/b2c_api/"
    _collection_name = CHRONOVET_COLLECTION
    _default_auth = "api_key"

    @classmethod
    def _get_b2c_backend_from_request(cls):
        backend_model = request.env["alc.b2c.backend"]
        return backend_model._get_from_http_request()

    def _get_component_context(self):
        """
        This method adds into the component context:
        * the b2c_backend
        """
        res = super(RestController, self)._get_component_context()
        res["b2c_backend"] = self._get_b2c_backend_from_request()
        return res
