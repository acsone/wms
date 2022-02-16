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
            for index in rec.index_ids:
                with rec.work_on(rec._name, index=index) as work:
                    adapter = work.component(usage="se.backend.adapter")
                    return adapter.put_ads(ads)
            ads.write({"sync_state": "done"})

    def synchronize_ads(self):
        self.export_ads()

    @api.model
    def cron_synchronize_ads(self):
        self.search([]).synchronize_ads()
