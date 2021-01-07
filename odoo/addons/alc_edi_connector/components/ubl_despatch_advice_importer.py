# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import Job


class UblDespatchAdviceImporter(Component):
    """ Synchronizer for importing data from a backend to Odoo """

    _name = "ubl.despatch.advice.importer"
    _inherit = ["edi.importer"]
    _apply_on = "stock.move"
    _usage = "ubl.despatch.advice.importer"

    def execute(self):
        wizard = self.env["despatch.advice.import"]
        for filename, content in self.backend_adapter.pull():
            description = _("Import Despatch Advice %s from %s") % (
                filename,
                self.backend_record.name,
            )
            attachment = self.env["ir.attachment"].create(
                {
                    "name": filename,
                    "datas": base64.b64encode(content),
                    "datas_fname": filename,
                }
            )
            new_job = wizard.with_delay(description=description).process_attachment(
                attachment
            )
            queue_job = Job.db_record_from_uuid(self.env, new_job.uuid)
            attachment.write({"res_id": queue_job.id, "res_model": queue_job._name})
