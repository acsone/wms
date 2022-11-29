# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.queue_job.job import job


class SeBackendElasticsearch(models.Model):
    _inherit = "se.backend.elasticsearch"

    @job(default_channel="root.search_engine.prepare_batch_export")
    def export_ads(self, ads=None):
        for rec in self:
            ads = ads or rec.env["alc.eshop.ads"]._get_ads_to_sync()
            for index in rec.index_ids.filtered(
                lambda i: i.model_id.model == "alc.eshop.ads"
            ):
                with rec.work_on(rec._name, index=index) as work:
                    adapter = work.component(usage="se.backend.adapter")
                    self._export_ads(adapter=adapter, ads=ads)
                    self._cleanup_obsolete_adds(adapter)
            ads.write({"sync_state": "done"})

    @api.model
    def _export_ads(self, adapter, ads):
        adapter.put_ads(ads)

    @api.model
    def _cleanup_obsolete_adds(self, adapter):
        lang = adapter.work.index.lang_id
        existing_ids = self.env["alc.eshop.ads"]._get_active_ads(lang=lang).ids
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

    def synchronize_ads(self):
        self.export_ads()

    @api.model
    def cron_synchronize_ads(self):
        self.search([]).synchronize_ads()
