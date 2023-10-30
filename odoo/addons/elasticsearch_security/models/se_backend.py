# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from opensearchpy import OpenSearch

from odoo import fields

from odoo.addons.connector_elasticsearch.models.se_backend import SeBackend

from .elasticsearch_role import ElasticSearchRole


class SeBackendElasticsearch(SeBackend):

    opensearch_user = fields.Char()
    opensearch_user_password = fields.Char()
    ssl = fields.Boolean(
        default=True,
        help="Verify SSL certificates. Only set to False in development environments.",
    )
    role_ids = fields.One2many[ElasticSearchRole](inverse_name="backend_id")

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update(
            {
                "opensearch_user": {},
                "opensearch_user_password": {},
                "ssl": {},
            }
        )
        return env_fields

    def synchronize_roles(self):
        return self.role_ids.put_roles()

    def _get_client_security(self):
        auth = (self.opensearch_user, self.opensearch_user_password)
        client = OpenSearch(
            hosts=[self.es_server_host], http_auth=auth, use_ssl=self.ssl
        )
        return client.security
