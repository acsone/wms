# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job


class EdiTaskDef(models.AbstractModel):
    _name = "edi.task.def"
    _description = "Edi Task Definition"

    backend_id = fields.Many2one(
        comodel_name="edi.backend", string="Backend Id", required=True, readonly=True
    )
    channel = fields.Selection(related="backend_id.channel", readonly=True, store=True)
    kind = fields.Selection(selection=[], string="Kind of EDI Process")
    display_name = fields.Char(compute="_compute_display_name")
    model_name = fields.Char(required=True)

    _sql_constraints = [
        ("backend_kind_uniq", "UNIQUE(backend_id, kind)", _("Kind must be unique"))
    ]

    @api.depends("backend_id", "kind")
    def _compute_display_name(self):
        kind_field = self._fields["kind"]
        kind_label_by_value = dict(kind_field._description_selection(self.env))
        for record in self:
            record.display_name = "{backend_name}: {kind_label}".format(
                backend_name=record.backend_id.name,
                kind_label=kind_label_by_value[record.kind],
            )

    @job(default_channel="root.background.edi")
    def execute(self, *args, **kwargs):
        for record in self:
            with record.backend_id.work_on(
                self.model_name, task_def=self, **kwargs
            ) as work:
                work.component(usage=self.kind).execute(*args, **kwargs)
        self._after_execute()

    def _after_execute(self):
        pass
