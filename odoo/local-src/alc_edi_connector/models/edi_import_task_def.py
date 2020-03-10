# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MODEL_NAME_BY_KIND = {"ubl.order.response.importer": "purchase.order"}


class EdiImportTaskDef(models.Model):
    _name = 'edi.import.task.def'
    _description = 'Edi Import Task Definition'
    _inherit = "edi.task.def"

    last_import_dt = fields.Datetime(string='Timestamp last import')

    kind = fields.Selection(
        selection=[
            ("ubl.order.response.importer", "Import UBL Order Response")
        ],
        string='Kind of EDI document',
    )

    path = fields.Char(
        help="If specified, is a sub path of the path specified on the backend"
    )
    file_matcher_pattern = fields.Char(
        help="Regexp used to identify the file to import"
    )

    model_name = fields.Char(compute="_compute_model_name")

    @api.constrains("channel", "file_matcher_pattern")
    def _check_file_matcher_pattern(self):
        for record in self:
            if record.channel == "sftp" and not record.file_matcher_pattern:
                raise ValidationError(
                    _(
                        "A File Matcher Pattern is required for task %s "
                        "with an SFTP backend"
                    )
                    % record.display_name
                )

    @api.depends("kind")
    def _compute_model_name(self):
        for record in self:
            record.model_name = MODEL_NAME_BY_KIND.get(record.kind)

    def _after_execute(self):
        self.write({"last_import_dt": fields.Datetime.now()})
