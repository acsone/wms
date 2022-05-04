# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.queue_job.job import job


class SeBackendElasticsearch(models.Model):
    _inherit = "se.backend.elasticsearch"

    @job(default_channel="root.search_engine.prepare_batch_export")
    def export_info_banners(self, banners=None):
        for rec in self:
            banners = banners or rec.env["alc.eshop.info.banner"]._get_banners_to_sync()
            for index in rec.index_ids.filtered(
                lambda i: i.model_id.model == "alc.eshop.info.banner"
            ):
                with rec.work_on(rec._name, index=index) as work:
                    adapter = work.component(usage="se.backend.adapter")
                    self._export_banners(adapter=adapter, banners=banners)
                    self._cleanup_obsolete_banners(adapter=adapter)
            banners.write({"sync_state": "done"})

    @api.model
    def _export_banners(self, adapter, banners):
        adapter.put_info_banners(banners)

    @api.model
    def _cleanup_obsolete_banners(self, adapter):
        existing_ids = self.env["alc.eshop.info.banner"]._get_active_banners().ids
        if existing_ids:
            q = {"bool": {"must_not": [{"terms": {"_id": existing_ids}}]}}
        else:
            q = {"match_all": {}}
        es_params = {"source": ["id"], "query": q}
        params = {"size": 10000}
        obsolete_ids = [
            r["id"] for r in adapter.search(es_params=es_params, params=params)
        ]
        if obsolete_ids:
            adapter.delete(obsolete_ids)

    def synchronize_info_banners(self):
        self.export_info_banners()

    @api.model
    def cron_synchronize_info_banners(self):
        self.search([]).synchronize_info_banners()
