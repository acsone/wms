# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging

import odoo
from odoo.http import Controller, Response, request, route

from ..facade import Facade

_logger = logging.getLogger(__name__)


class MagentoApi(Controller):
    def _authenticate(self, sudo_env, headers, expected_username):
        basic = headers["HTTP_AUTHORIZATION"]
        encoded = basic.replace("Basic ", "")
        decoded = base64.b64decode(encoded).decode("utf-8")
        # username and password are separated by a colon but the password can contain colons
        values = decoded.split(":")
        if len(values) < 2:
            raise ValueError(f"Invalid Basic Auth {decoded}")
        username, password = values[0], ":".join(values[1:])
        backend = sudo_env.ref("connector_keycloak.keycloak_backend")
        token = backend._get_token_from_user_info(username, password)
        assert token["token_type"] == "Bearer"
        return username

    def _get_partner(self, sudo_env, username):
        # username is case insenitive into keycloak and previously into magento
        # search on the username stored in lower case
        domain = [("keycloak_username", "=", (username or "").lower())]
        keycloak_partner = sudo_env["keycloak.user"].search(domain)
        keycloak_partner.ensure_one()  # reraised as user not found below
        return keycloak_partner.partner_id

    @route(
        [
            "/magento-api/<string:username>/<string:service>/",
            "/magento-api/<string:username>/<string:service>/<string:param>/<string:value>",
        ],
        type="http",
        auth="none",  # custom authentification step
        csrf=False,
    )
    def magento_api(self, username, service, **kwargs):
        headers = request.httprequest.environ
        sudo_env = request.env(user=odoo.SUPERUSER_ID)
        try:
            keycloak_username = self._authenticate(sudo_env, headers, username)
            partner = self._get_partner(sudo_env, keycloak_username)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Magento API: User %s not found.", username)
            return Response(response="User not found.", status=401)
        try:
            if request.httprequest.data:
                kwargs["data"] = request.httprequest.data
            if kwargs.get("param"):
                key = kwargs.pop("param")
                kwargs[key] = kwargs.pop("value")
            _logger.info("Magento API Args: %s, kwargs: %s", service, kwargs)
            facade = Facade.factory(sudo_env, partner, service)
            result, error, location = facade(**kwargs)
        except Exception as e:  # pylint: disable=broad-except
            _logger.exception("Magento API Call: %s", str(e))
            return Response(response="Cannot resolve API call.", status=202)
        status = 201 if request.httprequest.method == "POST" and not error else 200
        response = Response(response=error or result, status=status)
        if location:
            response.location = location
        return response
