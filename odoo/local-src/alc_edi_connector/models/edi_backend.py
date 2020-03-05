# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import _, api, fields, models
from odoo.exceptions import UserError

SFTP_TIMEOUT = 30


class EdiBackend(models.Model):

    _name = 'edi.backend'
    _description = 'Edi Backend'
    _inherit = 'connector.backend'

    name = fields.Char(required=True)
    channel = fields.Selection(
        [('sftp', 'ftp/sftp')], required=True, default="sftp"
    )
    hostname = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char()
    port = fields.Integer(default=22)
    pk_env_variable = fields.Char(
        'Private key environment variable',
        help='The name of the environment variable who '
        'contains the private sh key',
    )
    path_read = fields.Char()
    path_write = fields.Char()

    edi_import_task_def_ids = fields.One2many(
        comodel_name='edi.import.task.def',
        inverse_name='backend_id',
        string='Import Task Definition',
    )

    edi_export_task_def_ids = fields.One2many(
        comodel_name='edi.export.task.def',
        inverse_name='backend_id',
        string='Export Task Definition',
    )

    @contextmanager
    def work_on(self, model_name, task_def=None, **kwargs):
        _super = super(EdiBackend, self)
        with _super.work_on(model_name, task_def=task_def, **kwargs) as work:
            yield work

    @api.multi
    def test_connection(self):
        self.ensure_one()
        backend_adapter_usage = "{}.backend.adapter".format(self.type)
        with self.work_on("edi.backend") as work:
            backend_adapter = work.component(usage=backend_adapter_usage)
            backend_adapter.test_connection()

        raise UserError(_('Everything seems ok'))

    def _get_task(self, kind):
        """
        Get task def for type and kind...
        """
        return self.edi_export_task_def_ids.filtered(
            lambda a: a.kind == kind
        ) or self.edi_import_task_def_ids.filtered(lambda a: a.kind == kind)

    def send_order_document(self, purchase_order):
        self.ensure_one()
        task_def = self._get_task("ubl.order.exporter")
        if not task_def:
            raise UserError(
                _(
                    "UBL Oder Document Generation not configured on the backend %s"
                )
                % self.name
            )

        task_def.execute(purchase_order)
        return

    @api.model
    def cron_import(self):
        importers = self.search([]).mapped("edi_importer_ids")
        for importer in importers:
            description = _("Pull EDI %s from %s") % (
                importer.kind,
                importer.backend_id.name,
            )
            importer.with_delay(description=description).execute()
