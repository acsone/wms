# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, models

from odoo.addons.queue_job.job import identity_exact


class SeIndex(models.Model):

    _inherit = "se.index"

    @api.model
    def recompute_all_index(self, domain=None):
        if domain is None:
            domain = []
        domain.append(
            ("model_id", "!=", self.env.ref("alc_eshop_ads.model_alc_eshop_ads").id,)
        )
        return self.search(domain).recompute_all_binding()

    def force_batch_export(self):
        self.ensure_one()
        if self.is_alc_ads():
            self.env[self.model_id.model].search(
                [("sync_state", "!=", "to_update")]
            ).write({"sync_state": "to_update"})
            self.batch_export_ads()
        return super(SeIndex, self).force_batch_export()

    def batch_export_ads(self):
        for specific_backend in self.mapped("backend_id.specific_backend"):
            description = _(u"%s: Batch export EShop Ads") % specific_backend.name
            specific_backend.with_delay(
                identity_key=identity_exact, description=description
            ).export_ads()

    def is_alc_ads(self):
        return self.model_id == self.env.ref("alc_eshop_ads.model_alc_eshop_ads")
