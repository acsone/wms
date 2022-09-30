# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.queue_job.job import job


class SeBackendElasticsearch(models.Model):

    _inherit = "se.backend.elasticsearch"

    security = fields.Selection(
        [("xpack", "ElasticSearch Enterprise"), ("opensearch", "OpenSearch")]
    )
    ssl = fields.Boolean(
        default=True,
        help="Verify SSL certificates. Only set to False in development environments.",
    )

    role_ids = fields.One2many("elasticsearch.role", "backend_id")

    @property
    def _server_env_fields(self):
        env_fields = super(SeBackendElasticsearch, self)._server_env_fields
        env_fields.update({"ssl": {}})
        return env_fields

    def synchronize_roles(self):
        self.ensure_one()
        with self.work_on(self._name, index=None) as work:
            adapter = work.component(usage="se.backend.adapter")
            return adapter.put_roles()

    @job(default_channel="root.background.opensearch.role")
    def synchronize_role(self, role):
        self.ensure_one()
        with self.work_on(self._name, index=None) as work:
            adapter = work.component(usage="se.backend.adapter")
            return adapter.put_role(role)

    @job(default_channel="root.background.opensearch.role")
    def delete_role(self, role_name):
        self.ensure_one()
        with self.work_on(self._name, index=None) as work:
            adapter = work.component(usage="se.backend.adapter")
            return adapter.delete_role(role_name)
