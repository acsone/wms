# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import psycopg2

from odoo import _, api, exceptions, fields, models


class ESBBackendTimestamp(models.Model):
    _name = 'esb.backend.timestamp'
    _description = 'Keep time of last export'

    backend_id = fields.Many2one(
        comodel_name='esb.backend',
        string='Backend Id',
        required=True,
        readonly=True,
    )
    model = fields.Char(
        string='Model name',
        required=True,
        readonly=True,
    )
    kind = fields.Selection(
        selection=[('pharmacy', 'pharmacy'),
                   ('stock', 'stock'),
                   ('product', 'product')],
        string='Kind of export',
        readonly=True,
    )
    last_export = fields.Datetime(
        string='Timestamp last export'
    )
    export_filename = fields.Char(required=True,
                                  default='{name}_{date}.xml')
    path = fields.Char()
    writer = fields.Selection(
        selection=[('local', 'Local'),
                   ('sftp', 'sFTP')],
        default='sftp',
        required=True,
    )

    _sql_constraints = [
        ('model_kind_uniq', 'UNIQUE(model, kind)', _('Model must be unique')),
    ]

    @api.multi
    def export(self):
        """ Export a model from a cron """
        self.ensure_one()
        self._lock_timestamp()
        next_last_export = fields.Datetime.now()
        with self.backend_id.work_on(self.model, timestamp=self) as work:
            exporter = work.component(usage='record.exporter.cron')
            exporter.run(export_since=self.last_export)
        self.last_export = next_last_export

    @api.multi
    def _lock_timestamp(self):
        """ Lock the timestamp record

        Prevent 2 synchros to be launched at the same time.
        The lock is released at the commit of the transaction.

        """
        query = """
               SELECT id FROM esb_backend_timestamp
               WHERE id = %s
               FOR UPDATE NOWAIT
            """
        try:
            self.env.cr.execute(
                query, (self.id,)
            )
        except psycopg2.OperationalError:
            raise exceptions.UserError(
                _("The synchronization timestamp (%s) is currently locked, "
                  "probably due to an ongoing synchronization." %
                  (' '.join([self.model, self.timestamp.kind]),))
            )
