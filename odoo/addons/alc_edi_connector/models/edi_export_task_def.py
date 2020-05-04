# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import uuid

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MODEL_NAME_BY_KIND = {"ubl.order.exporter": "purchase.order"}


class EdiExportTaskDef(models.Model):
    _name = "edi.export.task.def"
    _description = "Edi Export Task Definition"
    _inherit = "edi.task.def"

    last_export_dt = fields.Datetime(string="Timestamp last export")

    kind = fields.Selection(
        selection=[("ubl.order.exporter", "Export UBL Order document")],
        string="Kind of EDI document",
    )

    path = fields.Char(
        help="If specified, is a sub path of the path specified on the backend"
    )

    export_filename = fields.Char(
        required=True,
        default="{name}_{date}.xml",
        help="The following place holders are available: name, id, date, time",
    )

    model_name = fields.Char(compute="_compute_model_name")

    @api.constrains("channel", "export_filename")
    def _check_export_filename(self):
        for record in self:
            if record.channel == "sftp" and not record.export_filename:
                raise ValidationError(
                    _(
                        "An export filename is required for task %s "
                        "with an SFTP backend"
                    )
                    % record.display_name
                )

    @api.depends("kind")
    def _compute_model_name(self):
        for record in self:
            record.model_name = MODEL_NAME_BY_KIND.get(record.kind)

    def filename(self, record=None):
        pattern = self.export_filename.strip()
        return pattern.format(
            name=record.name.replace(".", "_"),
            date=fields.Date.today().replace("-", ""),
            time=fields.Datetime.now().split(" ")[1].replace(":", ""),
            id=record.id if record else uuid.uuid4(),
        )

    def _after_execute(self):
        self.write({"last_export_dt": fields.Datetime.now()})
