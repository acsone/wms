# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from slugify import slugify

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.server_environment import serv_config

SFTP_TIMEOUT = 30


class EdiBackend(models.Model):

    _name = "edi.backend"
    _description = "Edi Backend"
    _inherit = "connector.backend"

    key = fields.Char(compute="_compute_key")
    name = fields.Char(required=True)
    channel = fields.Selection(
        [("sftp", "ftp/sftp")],
        required=True,
        default="sftp",
        compute="_compute_from_config",
    )
    hostname = fields.Char(required=True, compute="_compute_from_config")
    username = fields.Char(required=True, compute="_compute_from_config")
    password = fields.Char(compute="_compute_from_config")
    port = fields.Integer(default=22, compute="_compute_from_config")
    pk_env_variable = fields.Char(
        "Private key environment variable",
        help="The name of the environment variable who " "contains the private sh key",
        compute="_compute_from_config",
    )
    path_read = fields.Char(compute="_compute_from_config")
    path_write = fields.Char(compute="_compute_from_config")

    edi_import_task_def_ids = fields.One2many(
        comodel_name="edi.import.task.def",
        inverse_name="backend_id",
        string="Import Task Definition",
    )

    edi_export_task_def_ids = fields.One2many(
        comodel_name="edi.export.task.def",
        inverse_name="backend_id",
        string="Export Task Definition",
    )

    @contextmanager
    def work_on(self, model_name, task_def=None, **kwargs):
        _super = super(EdiBackend, self)
        with _super.work_on(model_name, task_def=task_def, **kwargs) as work:
            yield work

    @api.multi
    def test_connection(self):
        self.ensure_one()
        backend_adapter_usage = u"{}.backend.adapter".format(self.channel)
        with self.work_on("edi.backend") as work:
            backend_adapter = work.component(usage=backend_adapter_usage)
            backend_adapter.test_connection()

        raise UserError(_("Everything seems ok"))

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
                _("UBL Oder Document Generation not configured on the backend %s")
                % self.name
            )

        task_def.execute(purchase_order)

    @api.model
    def cron_import(self):
        importers = self.search([]).mapped("edi_import_task_def_ids")
        for importer in importers:
            description = _("Pull EDI %s") % (importer.display_name,)
            importer.with_delay(description=description).execute()

    @api.depends("name")
    def _compute_key(self):
        self.ensure_one()
        self.key = "edi_backend_" + slugify(self.name, separator="_", lowercase=True)

    def _compute_from_config(self):
        self.ensure_one()
        for section in serv_config.sections():
            if self.key and section.startswith(self.key):
                self.channel = serv_config.get(section, "channel")
                self.hostname = serv_config.get(section, "hostname")
                self.username = serv_config.get(section, "username")
                self.password = serv_config.get(section, "password")
                self.port = serv_config.get(section, "port")
                self.pk_env_variable = serv_config.get(section, "pk_env_variable")
                self.path_read = serv_config.get(section, "path_read")
                self.path_write = serv_config.get(section, "path_write")
