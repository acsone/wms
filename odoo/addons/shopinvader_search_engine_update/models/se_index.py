# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    continuous_update = fields.Boolean(related="model_id.continuous_update")

    def _get_model_domain(self, continuous):
        domain = [("index_id", "in", self.ids)]
        return domain + [("to_update", "=", "true")] if continuous else domain

    @api.model
    def cron_recompute_all_continuous(self, force_export=False, batch_size=500):
        self.search([])._cron_recompute_all(
            continuous=True, force_export=force_export, batch_size=batch_size
        )

    @api.model
    def cron_recompute_all_batch(self, force_export=False, batch_size=500):
        self.search([])._cron_recompute_all(
            continuous=False, force_export=force_export, batch_size=batch_size
        )

    @api.model
    def _cron_recompute_all(self, continuous, force_export=False, batch_size=500):
        # recompute_all_binding should be refactored to accept a configurable domain...
        filter_continuous = lambda m: m.continuous_update == continuous
        target_models = self.mapped("model_id").filtered(filter_continuous)
        for target_model in target_models:
            indexes = self.filtered(lambda r, m=target_model: r.model_id == m)
            domain = indexes._get_model_domain(continuous)
            bindings = self.env[target_model.model].search(domain)
            for batch in bindings.batch(batch_size):
                description = _("Recompute json for %s record(s).") % len(batch)
                batch.with_delay(description=description)._jobify_recompute_json(
                    force_export=force_export
                )
                if continuous:
                    batch.write({"to_update": "scheduled"})

    @api.model
    def cron_export_all_continuous(self, domain=None):
        domain = domain or []
        continuous_indices = self.search(domain).filtered("continuous_update")
        domain += [("id", "in", continuous_indices.ids)]
        self.generate_batch_export_per_index(domain)

    @api.model
    def cron_export_all_batch(self, domain=None):
        domain = domain or []
        continuous_indices = self.search(domain).filtered("continuous_update")
        domain += [("id", "not in", continuous_indices.ids)]
        self.generate_batch_export_per_index(domain)
