# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import _, api, exceptions, fields, models


class ESBBackend(models.Model):
    _name = 'esb.backend'
    _description = 'ESB Backend'
    _inherit = 'connector.backend'

    sftp_location = fields.Char(string='SFTP Location',
                                compute='_compute_from_env')
    timestamp_ids = fields.One2many(
        comodel_name='esb.backend.timestamp',
        inverse_name='backend_id',
        string='Synchronizations',
    )

    @api.depends()
    def _compute_from_env(self):
        for record in self:
            record.sftp_location = os.getenv('ODOO_ESB_SFTP_LOCATION', '')

    @api.model
    def get_singleton(self):
        return self.env.ref('connector_esb.esb_backend_config')

    @api.model
    def create(self, vals):
        existing = self.search([])
        if existing:
            raise exceptions.UserError(
                _('Only 1 ESB configuration is allowed.')
            )
        return super(ESBBackend, self).create(vals)

    def _get_timestamp(self, model, kind=None):
        return self.env['esb.backend.timestamp'].search(
            [('backend_id', '=', self.id),
             ('model', '=', model),
             ('kind', '=', kind)]
        )

    @api.model
    def cron_export_product(self):
        backend = self.get_singleton()
        backend._get_timestamp('product.product').export()
