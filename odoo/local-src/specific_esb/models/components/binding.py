# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api
from odoo.addons.queue_job.job import job, related_action

from ...fields import AutoSetupMany2one


class ESBBinding(models.AbstractModel):
    _name = 'esb.binding'
    _inherit = 'external.binding'
    _description = 'ESB Binding (abstract)'

    backend_id = fields.Many2one(
        comodel_name='esb.backend',
        string='ESB Backend',
        required=True,
        ondelete='restrict',
    )
    odoo_id = AutoSetupMany2one(
        comodel_name='esb.binding',
        string='Odoo record',
        required=True,
        index=True,
        ondelete='restrict'
    )
    external_id = fields.Integer(string='External ID', index=True)

    @job(default_channel='root.esb')
    @related_action(action='related_action_unwrap_binding')
    @api.model
    def import_record(self, backend, external_id, force=False):
        """Import an ESB record."""
        backend.ensure_one()
        # TODO

    @job(default_channel='root.esb')
    @related_action(action='related_action_unwrap_binding')
    @api.multi
    def export_record(self, fields=None):
        """Export an ESB record."""
        self.ensure_one()
        # TODO
