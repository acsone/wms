# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import Job


class UblOrderResponseImporter(Component):
    """ Synchronizer for importing data from a backend to Odoo """

    _name = 'ubl.order.response.importer'
    _inherit = ['edi.importer']
    _apply_on = 'purchase.order'
    _usage = 'ubl.order.response.importer'

    def execute(self):
        wizard = self.env["order.response.import"]
        for filename, content in self.backend_adapter.pull():
            description = _("Import Order Response %s from %s") % (
                filename,
                self.backend_record.name,
            )
            new_job = wizard.with_delay(
                description=description
            ).process_content(content, filename)
            queue_job = Job.db_record_from_uuid(self.env, new_job.uuid)
            self.env['ir.attachment'].create(
                {
                    'name': filename,
                    'res_id': queue_job.id,
                    'res_model': queue_job._name,
                    'datas': base64.b64encode(content),
                    'datas_fname': filename,
                }
            )
