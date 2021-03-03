# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import psycopg2

from odoo import _, api, exceptions, fields, models

from odoo.addons.component.exception import NoComponentError


class ESBBackendTimestamp(models.Model):
    _name = "esb.backend.timestamp"
    _description = "Keep time of last export"

    backend_id = fields.Many2one(
        comodel_name="esb.backend", string="Backend Id", required=True, readonly=True
    )
    model = fields.Char(string="Model name", required=True, readonly=True)
    kind = fields.Selection(
        selection=[
            (opt,) * 2
            for opt in [
                "pharmacy",
                "stock",
                "product",
                "customer",
                "customer.address",
                "product.price",
                "promotion.alcyon",
                "special.promotion",
                "buyx.gety",
                "documents",
                "stock.update",
                "stock.update.single",
            ]
        ],
        string="Kind of export",
        readonly=True,
    )
    last_export = fields.Datetime(string="Timestamp last export")
    max_records = fields.Integer(
        default=0, string="Maximum of records to export at once."
    )
    export_filename = fields.Char(required=True, default="{name}_{date}.xml")
    path = fields.Char()
    writer = fields.Selection(
        selection=[("local", "Local"), ("sftp", "sFTP"), ("webservice", "WebService")],
        default="sftp",
        required=True,
    )

    _sql_constraints = [
        ("model_kind_uniq", "UNIQUE(model, kind)", _("Model must be unique"))
    ]

    @api.multi
    def export(self):
        """ Run an export for a timestamp from a cron.

        """
        self.ensure_one()
        self._lock_timestamp()
        next_last_export = fields.Datetime.now()
        with self.backend_id.work_on(self.model, timestamp=self) as work:
            try:
                exporter = work.component(usage="record.exporter.cron")
            except NoComponentError:
                raise exceptions.UserError(
                    _("This export can not be triggered manually.")
                )
            result = exporter.run(
                export_since=self.last_export, max_records=self.max_records
            )
            if self.writer == "webservice":
                self.last_export = result or next_last_export
            else:
                self.last_export = next_last_export

    @api.multi
    def export_period(self):
        action = {
            "type": "ir.actions.act_window",
            "name": "Export: %s" % self.kind,
            "res_model": "esb.period.exporter",
            "context": [("active_ids", "=", self.ids)],
            "view_mode": "form",
            "target": "new",
        }
        return action

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
            self.env.cr.execute(query, (self.id,))
        except psycopg2.OperationalError:
            raise exceptions.UserError(
                _(
                    "The synchronization timestamp (%s) is currently locked, "
                    "probably due to an ongoing synchronization."
                )
                % (" ".join([self.model, self.kind]),)
            )
