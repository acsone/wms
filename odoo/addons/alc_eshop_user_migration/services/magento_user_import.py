# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re

import requests
from werkzeug.exceptions import Forbidden, NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class MagentoUserImport(Component):
    """REST endpoints used by 'keycloak-user-migration' to import users from
    legacy magento system.

    see https://github.com/daniel-frak/keycloak-user-migration
    """

    _inherit = "base.rest.service"
    _name = "alc.eshop.magento.user.import"
    _collection = "magento.account.validator"
    _usage = "magento_user_import"

    @restapi.method(
        [(["/<string:username>"], "GET")], auth="magento_migration_bearer_token",
    )
    def get(self, username):
        _logger.info("Check if magento user %s exists.", username)
        magento_user = self._get_magento_user(username=username)
        if not magento_user:
            _logger.info("Magento user %s not found into odoo.", username)
            raise NotFound()
        if magento_user.activated:
            _logger.info("Magento user %s already activated.", username)
            raise NotFound()
        payload = magento_user._to_keycloak_user_payload()
        magento_user._finalize_registration()
        return payload

    @restapi.method(
        [(["/<string:username>"], "POST")],
        input_param=restapi.CerberusValidator("_check_password_input_schema"),
        auth="magento_migration_bearer_token",
    )
    def check_password(self, username, password):
        _logger.info("Validate password for user %s.", username)
        magento_user = self._get_magento_user(username=username)
        if not magento_user:
            _logger.info("Magento user %s not found into odoo.", username)
            raise NotFound()
        s = requests.session()
        main_url = self.magento_url
        html_data = s.get(
            main_url + "/fr/fragment/ajax/get/identifier/dynamic/",
            headers={"Content-Type": "application/json"},
        )
        formkey_content = html_data.json()["formkey_content"]
        form_key = re.findall(r'value="(.[^"]+)"', formkey_content)[0]

        login_route = main_url + "/fr/customer/account/loginPost/"

        login_payload = {
            "form_key": form_key,
            "login[username]": username,
            "login[password]": password,
        }
        login_req = s.post(login_route, data=login_payload)
        login_ok = "incorrect" not in login_req.content
        if not login_ok:
            _logger.info("Wrong password for user %s.", username)
            raise Forbidden()

        # try to access to a secured page to be sure that the login is successful since
        # login always return HTTP 200
        account_url = main_url + "/fr/alcyon_customer/account/profile/"
        html_account = s.get(account_url)
        account_ok = "Mon compte" in html_account.content
        if not account_ok:
            _logger.info("Wrong password for user %s.", username)
            raise Forbidden()
        return {}

    def _check_password_input_schema(self):
        return {"password": {"required": True, "nullable": False, "type": "string"}}

    def _get_magento_user(self, username):
        return self.env["magento.user"].sudo().search([("username", "=", username)])

    @property
    def magento_url(self):
        config_param = self.env["ir.config_parameter"].sudo()
        return config_param.sudo().get_param("alc_eshop_user_migration.magento_url")
