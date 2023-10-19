# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import re

from werkzeug.exceptions import Unauthorized

from odoo import SUPERUSER_ID, api, models, registry as registry_get
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.tools import consteq, ustr

_logger = logging.getLogger(__name__)

AUTHORIZATION_RE = re.compile(r"^Bearer ([^ ]+)$")


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_magento_migration_bearer_token(cls):
        token = cls._get_bearer_token()
        assert token
        registry = registry_get(request.db)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            config_param = env["ir.config_parameter"].sudo()
            expected_token = config_param.get_param(
                "alc_eshop_user_migration.bearer_token"
            )
            if consteq(ustr(token), ustr(expected_token)):
                return True
        raise AccessDenied()

    @classmethod
    def _get_bearer_token(cls):
        # https://tools.ietf.org/html/rfc2617#section-3.2.2
        authorization = request.httprequest.environ.get("HTTP_AUTHORIZATION")
        if not authorization:
            _logger.info("Missing Authorization header.")
            raise Unauthorized()
        # https://tools.ietf.org/html/rfc6750#section-2.1
        mo = AUTHORIZATION_RE.match(authorization)
        if not mo:
            _logger.info("Malformed Authorization header.")
            raise Unauthorized()
        return mo.group(1)
