# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import os
import shutil
import tempfile
import time

import unicodecsv as csv

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CSVFileExportLogger(models.Model):
    _name = "csv.file.export.logger"
    _inherit = "csv.file.logger"
    _order = "create_date DESC"
    _rec_name = "date_start"

    file_id = fields.Many2one("csv.file.export", required=True, string="File")


class CSVFileExport(models.Model):
    _inherit = "csv.file"
    _name = "csv.file.export"

    logger_ids = fields.One2many(
        "csv.file.export.logger", "file_id", string="Exports", readonly=True
    )
    last_logger = fields.Many2one(
        "csv.file.export.logger",
        compute="_compute_last_action",
        readonly=True,
        store=True,
    )
    last_logger_datetime = fields.Datetime(
        "Date last export", compute="_compute_last_action", readonly=True
    )
    last_logger_state = fields.Selection(
        [("success", "Success"), ("error", "Error")],
        "Last export state",
        compute="_compute_last_action",
        readonly=True,
    )

    @api.depends("logger_ids")
    def _compute_last_action(self):
        for csv_file in self:
            if csv_file.logger_ids:
                csv_file.last_logger = csv_file.logger_ids[0].id
                csv_file.last_logger_datetime = csv_file.logger_ids[0].date_start
                csv_file.last_logger_state = csv_file.logger_ids[0].state

    @api.model
    def execute_all_exports(self):
        exports = self.search([])

        exports.execute_exports()

    @api.multi
    def execute_exports(self, limit=0):
        """
        Execute all exports
        :param limit:
        :return:
        """
        tempdir_path = tempfile.mkdtemp()

        # There is a bug with Odoo. If you call a method with optional
        # parameter from a button (type object), the context is send
        # in the first param.
        if isinstance(limit, dict):
            limit = 0

        for csv_export in self:
            _logger.info("Start export %s", csv_export.name)
            time_start = time.time()
            logger = csv_export.logger_ids.create(
                {"file_id": csv_export.id, "date_start": fields.Datetime.now()}
            )

            filename_pattern = self.get_filename_pattern(csv_export.filename)
            tempfile_path = os.path.join(tempdir_path, filename_pattern)

            try:
                #################
                # Check OUT path #
                ##################
                export_path = csv_export.folder_out
                is_directory = self.check_directory(export_path, create_if_missing=True)
                if not is_directory:
                    raise UserError(
                        _("The folder %s doesn't exist on the source") % export_path
                    )

                destination_path = os.path.join(export_path, filename_pattern)

                header, rows = getattr(csv_export, csv_export.method)(limit)

                with open(tempfile_path, "wb") as csv_file:
                    writer = csv.writer(
                        csv_file,
                        delimiter=str(csv_export.delimiter),
                        encoding=csv_export.file_encoding,
                    )
                    writer.writerow(header)
                    writer.writerows(rows)

                csv_export.put_file(tempfile_path, destination_path)

                time_end = time.time()
                duration = time_end - time_start
                logger.write(
                    {
                        "date_end": fields.Datetime.now(),
                        "nbr_lines": len(rows),
                        "message": "File saved to %s" % destination_path,
                        "duration": duration,
                    }
                )
            except Exception as e:
                _logger.error(str(e))
                logger.write({"state": "error", "message": str(e)})

        shutil.rmtree(tempdir_path)
