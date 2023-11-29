# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from opensearchpy import OpenSearch

from odoo import fields

from odoo.addons.connector_elasticsearch.models.se_backend import SeBackend

from .elasticsearch_role import ElasticSearchRole


class SeBackendElasticsearch(SeBackend):

    role_ids = fields.One2many[ElasticSearchRole](inverse_name="backend_id")

    def synchronize_roles(self):
        return self.role_ids.put_roles()

    def _get_client_security(self):
        auth = (self.es_user, self.es_password)
        client = OpenSearch(
            hosts=[self.es_server_host], http_auth=auth, use_ssl=self.ssl
        )
        return client.security
