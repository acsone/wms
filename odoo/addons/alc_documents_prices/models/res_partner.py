# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models

from odoo.addons.queue_job.job import job


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        res.jobify_process_dossier()
        return res

    @api.model
    def dossier_watched_fields(self):
        return [
            "supplier_promotion_sale_allowed",
            "discount_pricelist_id",
            "property_product_pricelist",
        ]

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if any(field in vals for field in self.dossier_watched_fields()):
            self.jobify_process_dossier()
        return res

    def jobify_process_dossier(self):
        for partner in self.filtered("needs_dossier"):
            description = _("Process dossier for partner %s") % partner.name
            partner.with_delay(description=description)._process_dossier()

    @job(default_channel="root.background.process")
    def _process_dossier(self):
        document_model = self.env["alc.document"]
        for partner in self.filtered("needs_dossier"):
            # we remove everything, so it 'invalidates the cache'
            # thus we don't need to check values before/after etc
            domain = [
                ("partner_id", "=", partner.id),
                ("compute", "in", ["discount", "pricelist"]),
            ]
            to_remove = document_model.search(domain)
            to_remove.mapped("attachment_id").unlink()
            to_remove.sudo().unlink()
            document_model._create_pricelist(partner)
            if partner.supplier_promotion_sale_allowed:
                document_model._create_discount(partner)

    @api.model
    @job(default_channel="root.background.process")
    def _migrate_jobify_process_dossier(self, offset, id_stop, batch_size):
        """Process batch_size partners, and create a job for the rest."""
        domain = [("id", "<=", id_stop)]
        to_process = self.search(domain, offset=offset, order="id", limit=batch_size)
        to_process.jobify_process_dossier()
        new_start = offset + batch_size
        if new_start < id_stop:
            self.with_delay(priority=50)._migrate_jobify_process_dossier(
                new_start, id_stop, batch_size
            )
