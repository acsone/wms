# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import os
import re
import shutil
import tempfile
import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CSVFileImportLogger(models.Model):
    _name = "csv.file.import.logger"
    _inherit = "csv.file.logger"
    _order = "create_date DESC"
    _rec_name = "date_start"

    file_id = fields.Many2one("csv.file.import", required=True, string="File")


class CSVFileImport(models.Model):
    _inherit = "csv.file"
    _name = "csv.file.import"

    folder_in = fields.Char("Folder IN", required=True)
    folder_failure = fields.Char("Folder FAILURE", required=True)
    logger_ids = fields.One2many(
        "csv.file.import.logger", "file_id", string="Import", readonly=True
    )
    last_logger = fields.Many2one(
        "csv.file.import.logger",
        compute="_compute_last_action",
        readonly=True,
        store=True,
    )
    last_logger_datetime = fields.Datetime(
        "Date last import", compute="_compute_last_action", readonly=True
    )
    last_logger_state = fields.Selection(
        [("success", "Success"), ("error", "Error")],
        "Last import state",
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
    def execute_all_imports(self):
        imports = self.search([])

        imports.execute_imports()

    @api.multi  # noqa: C901
    def execute_imports(self):
        """
        Execute all imports
        :return:
        """
        tempdir_path = tempfile.mkdtemp()

        for csv_import in self:
            _logger.info("Start import %s", csv_import.name)
            time_start = time.time()
            logger = csv_import.logger_ids.create(
                {"file_id": csv_import.id, "date_start": fields.Datetime.now()}
            )

            try:
                #################
                # Check IN path #
                #################
                import_path = csv_import.folder_in
                is_directory = self.check_directory(import_path, create_if_missing=True)

                if not is_directory:
                    raise UserError(
                        _("The folder %s doesn't exist on the source") % import_path
                    )

                #################
                # Check OUT path #
                ##################
                import_out_path = csv_import.folder_out
                is_directory = self.check_directory(
                    import_out_path, create_if_missing=True
                )
                if not is_directory:
                    raise UserError(
                        _("The folder %s doesn't exist on the source") % import_out_path
                    )

                ######################
                # Check FAILURE path #
                ######################
                import_failure_path = csv_import.folder_failure
                is_directory = self.check_directory(
                    import_failure_path, create_if_missing=True
                )
                if not is_directory:
                    raise UserError(
                        _("The folder %s doesn't exist on the source")
                        % import_failure_path
                    )

                # Retrieve files
                filename_pattern = self.get_filename_pattern(csv_import.filename)
                files_to_import = []
                files_imported = []
                files_not_imported = []
                for filename in self.get_all_files(import_path):
                    file_path = os.path.join(import_path, filename)
                    if re.match(filename_pattern, filename):
                        files_to_import.append(file_path)

                for file_to_import in files_to_import:
                    _logger.info("Import file %s", file_to_import)
                    filename = file_to_import.split("/")[-1]
                    content = self.get_file_content(
                        file_to_import, encoding=self.file_encoding
                    )

                    import_failure_file = os.path.join(import_failure_path, filename)
                    import_done_file = os.path.join(import_out_path, filename)

                    # Execute the method to import content
                    is_imported, import_message = getattr(
                        csv_import, csv_import.method
                    )(content)

                    if is_imported:
                        files_imported.append((file_to_import, import_message))
                        self.move_file(file_to_import, import_done_file)
                    else:
                        files_not_imported.append((file_to_import, import_message))
                        self.move_file(file_to_import, import_failure_file)

                time_end = time.time()
                duration = time_end - time_start

                # Generate the message (import' summary)
                if not files_imported and not files_not_imported:
                    message = "No files imported"
                else:
                    message = ""
                    if files_imported:
                        message += "Files imported:\n"
                        for file_imported, import_message in files_imported:
                            message += u"- {}: {}\n".format(
                                file_imported, import_message
                            )
                    if files_not_imported:
                        message += "Files not imported:\n"
                        for (file_not_imported, import_message) in files_not_imported:
                            message += u"- {}: {}\n".format(
                                file_not_imported, import_message
                            )

                # Compute the state
                if not files_imported and files_not_imported:
                    state = "error"
                elif files_imported and files_not_imported:
                    state = "partial"
                else:
                    state = "success"

                logger.write(
                    {
                        "date_end": fields.Datetime.now(),
                        "nbr_lines": len(files_to_import),
                        "message": message,
                        "duration": duration,
                        "state": state,
                    }
                )
            except Exception as e:
                _logger.error(str(e))
                logger.write({"state": "error", "message": str(e)})

        shutil.rmtree(tempdir_path)
