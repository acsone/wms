# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main
from odoo.http import request

from ..services.base_chronovet_service import CHRONOVET_COLLECTION


class RestController(main.RestController):
    _root_path = "/chronovet_api/"
    _collection_name = CHRONOVET_COLLECTION
    _default_auth = "api_key"

    def _get_component_context(self):
        """
        This method adds into the component context:
        * the chronovet_backend
        """
        res = super(RestController, self)._get_component_context()
        res["chronovet_backend"] = request.env["alc.chronovet.backend"].get_singleton()
        return res
