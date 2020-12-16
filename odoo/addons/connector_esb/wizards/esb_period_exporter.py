# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.addons.component.exception import NoComponentError


class EsbPeriodExporter(models.TransientModel):

    _name = "esb.period.exporter"

    backend_timestamp_id = fields.Many2one(
        comodel_name="esb.backend.timestamp",
        string="Backend Id",
        required=True,
        readonly=True,
        default=lambda a: a._default_backend_timestamp_id(),
    )
    export_from = fields.Datetime(string="From", required=True)
    export_to = fields.Datetime(string="To")

    @api.model
    def _default_backend_timestamp_id(self):
        return (
            self.env["esb.backend.timestamp"]
            .browse(self.env.context.get("active_ids"))
            .id
        )

    def doit(self):
        self.ensure_one()
        bt = self.backend_timestamp_id
        with bt.backend_id.work_on(bt.model, timestamp=bt) as work:
            try:
                exporter = work.component(usage="record.exporter.cron")
            except NoComponentError:
                raise exceptions.UserError(
                    _("This export can not be triggered manually.")
                )
            return exporter.run(
                export_since=self.export_from,
                export_to=self.export_to,
                max_records=bt.max_records,
            )
