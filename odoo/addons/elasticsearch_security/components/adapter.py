# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

import requests

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ElasticsearchAdapter(Component):
    _inherit = "elasticsearch.adapter"

    def put_roles(self):
        for role in self.backend_record.role_ids:
            self.put_role(role)

    def put_role(self, role):
        """Create or update a role on ES or OpenSearch"""
        # if you get 'Could not parse content of request' check the embedded query
        # they should have \\", which in the xml files should be written as \"
        # (the slashes are automatically escaped during the loading process).
        # Note that the Security DSL accepted by ES and OpenSearch are completely
        # different.
        if self.backend_record.security == "xpack":
            client = self._get_es_client()
            client.security.put_role(role.name, role.body)
            # TODO: would then need a new field to specify mapping body
            # client.security.put_role_mapping(role.name, mapping_body)
        else:
            host = self.backend_record.es_server_host
            host = host if host.endswith("/") else host + "/"
            base_url = host + "_plugins/_security/api/"
            url = base_url + "roles/" + role.name
            auth = (self.backend_record.es_user, self.backend_record.es_password)
            headers = {"Content-Type": "application/json"}
            ssl = self.backend_record.ssl
            data = role.body
            r = requests.put(url=url, data=data, auth=auth, headers=headers, verify=ssl)
            if r.status_code not in [200, 201]:
                msg = _("Could not put role %s. Original error: %s")
                raise ValidationError(msg % (role.name, r.content))
            url = base_url + "rolesmapping/" + role.name
            data = json.dumps({"backend_roles": role.get_backend_roles()})
            r = requests.put(url=url, data=data, auth=auth, headers=headers, verify=ssl)
            if r.status_code not in [200, 201]:
                msg = _("Could not put role mapping for %s. Original error: %s")
                raise ValidationError(msg % (role.name, r.content))

    def delete_role(self, role_name):
        host = self.backend_record.es_server_host
        host = host if host.endswith("/") else host + "/"
        base_url = host + "_plugins/_security/api/"
        url = base_url + "roles/" + role_name
        auth = (self.backend_record.es_user, self.backend_record.es_password)
        headers = {"Content-Type": "application/json"}
        ssl = self.backend_record.ssl
        r = requests.delete(url=url, auth=auth, headers=headers, verify=ssl)
        if r.status_code not in [200, 201, 404]:
            # 404 means the role already doesn't exist, so it should be fine
            msg = _("Could not delete role %s. Original error: %s")
            raise ValidationError(msg % (role_name, r.content))
