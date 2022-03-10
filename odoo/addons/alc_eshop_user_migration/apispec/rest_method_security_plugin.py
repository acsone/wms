# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from apispec import BasePlugin


class RestMethodSecurityPlugin(BasePlugin):
    def __init__(self, service):
        super(RestMethodSecurityPlugin, self).__init__()
        self._service = service

    def init_spec(self, spec):
        res = super(RestMethodSecurityPlugin, self).init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version
        return res

    def operation_helper(self, path=None, operations=None, **kwargs):
        if (
            "magento_migration_bearer_token"
            not in self.spec.components._security_schemes
        ):
            jwt_scheme = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "String",
                "name": "magento_migration_bearer_token",
                "description": "Enter Magento Migration Bearer Token ** only **",
            }
            self.spec.components.security_scheme(
                "magento_migration_bearer_token", jwt_scheme
            )
        routing = kwargs.get("routing")
        if not routing:
            super(RestMethodSecurityPlugin, self).operation_helper(
                path, operations, **kwargs
            )
        if not operations:
            return
        auth = routing.get("auth", self.spec._params.get("default_auth"))
        if auth and auth == "magento_migration_bearer_token":
            for _method, params in operations.items():
                security = params.setdefault("security", [])
                security.append({"magento_migration_bearer_token": []})
