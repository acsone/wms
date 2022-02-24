# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.queue_job.job import job


class Attachment(models.Model):

    _inherit = "ir.attachment"

    @api.model
    def create(self, vals):
        res = super(Attachment, self).create(vals)
        self.env["alc.document"].jobify_process_dossier(res)
        return res

    @api.model
    @job(default_channel="root.background.process")
    def _migrate_jobify_process_dossier(self, offset, id_stop, batch_size):
        """Process batch_size attachments, and create a job for the rest."""
        domain = [("id", "<=", id_stop)]
        to_process = self.search(domain, offset=offset, order="id", limit=batch_size)
        for attachment in to_process:
            self.env["alc.document"].jobify_process_dossier(attachment)
        new_start = offset + batch_size
        if new_start < id_stop:
            self.with_delay(priority=50)._migrate_jobify_process_dossier(
                new_start, id_stop, batch_size
            )
