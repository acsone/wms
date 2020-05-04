# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import os
import re
import shutil
from contextlib import contextmanager
from datetime import datetime
from io import StringIO

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CSVFile(models.Model):
    _name = "csv.file"

    name = fields.Char("Name", required=True)
    active = fields.Boolean("Active", default=True)
    filename = fields.Char("Filename", required=True)
    delimiter = fields.Char("Delimiter", required=True)
    folder_out = fields.Char("Folder OUT", required=True)
    method = fields.Char(required=True)
    file_encoding = fields.Char(required=True, default="utf_8")

    ftp_connector_id = fields.Many2one(
        "ftp.connector", string="FTP connector", required=False
    )

    _sql_constraints = [
        ("unique_csv_file", "UNIQUE(filename)", _("The file name must be unique."))
    ]

    @api.constrains("filename")
    def check_filename(self):
        for import_file in self:
            import_file.get_filename_pattern(self.filename)

    @api.model
    def get_filename_pattern(self, filename, now_overwrite=None):
        """
        This method will return the filename of the file to import.
        Often files to import have a structured format.

        ######## With a date ########
        The file to import is "20170924_Customers.csv"
            - 20170924 is the date of today
            - _Customers.csv is the fixed part
        To use the date in the filename you can use datetime directive.
        (https://docs.python.org/2/library/datetime
        .html#strftime-and-strptime-behavior)

        By default, the datetime of "now" will be used to format datetime
        directives. You can overwrite the datetime of now with
        the param "now_overwrite"
        In this example, the filename will be "%Y%m%d_Customers.csv"

        ######## Simple filename ########
        The file to import is "ImportCustomer.csv"
            - ImportCustomer is the fixed part
        In this example, the filename will be "ImportCustomer.csv"
        :param filename: The filename
        :param now_overwrite: To overwrite the datetime of now (used in tests)
        :return:
        """

        # Check if the filename contains the extension
        if "." not in filename:
            raise UserError(_("The filename must contain the extension"))

        # Use the datetime send in params or "now" (datetime)
        now = now_overwrite or datetime.now()

        # Datetime directives contain only "%" with a letter (eg: %Y, %m, ...)
        date_directive_regex = r"(%[a-zA-Z])"
        # To format date we will extract these directives
        result = re.findall(date_directive_regex, filename)
        # If the filename doesn't contain datetime directives
        # we can directly return the filename
        if not result:
            return filename

        # For each datetime directive (eg: %Y, %m, %d, ...), retrieve the value
        # and replace the directive by the value
        # Eg: the filename is %Y%m%d_customers.csv
        # The regex will return ['%Y', '%m', '%d']
        # First iteration: evaluation of %Y => 2017; replace %Y by 2017
        for date_format in result:
            try:
                value = now.strftime(date_format)
            except Exception:
                raise UserError(
                    _("The filename is not valid." 'Please check the part "%s"')
                    % date_format
                )

            filename = filename.replace(date_format, value)

        return filename

    @api.multi
    def check_directory(self, directory_path, create_if_missing=False):
        """
        Return True if the directory exist on the source.
        The method will create the directory if create_if_missing == True
        :param directory_path: The directory path
        :param create_if_missing: Create the directory
        if the directory doesn't exist
        :return: bool - True if the directory exist or False
        """
        self.ensure_one()

        if not self.ftp_connector_id:
            is_directory = os.path.isdir(directory_path)

            if not create_if_missing:
                return is_directory

            if not is_directory:
                os.makedirs(directory_path)

            return True
        elif self.ftp_connector_id.type == "sftp":
            with self.get_sftp_connector() as connector:
                try:
                    connector.listdir(directory_path)
                except IOError:
                    if create_if_missing:
                        connector.mkdir(directory_path)
                        return True
                    return False
                except Exception:
                    raise

            return True
        else:
            raise UserError(_("Unknown import type"))

    @api.multi
    def check_file(self, file_path):
        self.ensure_one()

        if not self.ftp_connector_id:
            return os.path.isfile(file_path)
        elif self.ftp_connector_id.type == "sftp":
            with self.get_sftp_connector() as connector:
                stat = connector.stat(file_path)
                if stat:
                    return True
                return False
        else:
            raise UserError(_("Unknown import type"))

    @api.multi
    def get_all_files(self, import_path):
        """
        Return a list of files name available on the source
        :param import_path: The path on the source
        :return: list - A list of file paths
        """
        self.ensure_one()

        if not self.ftp_connector_id:
            files = os.listdir(import_path)
        elif self.ftp_connector_id.type == "sftp":
            with self.get_sftp_connector() as connector:
                files = connector.listdir(import_path)
        else:
            raise UserError(_("Unknown import type"))

        return files

    @api.multi
    def get_file_content(self, file_path, encoding="utf_8"):
        """
        Return the file content (StringIO) from file_path
        :param file_path: The path of the file on the source
        :return: StringIO - The content of the file
        """
        self.ensure_one()

        if not self.ftp_connector_id:
            with open(file_path, "r") as f:
                content = StringIO(f.read().decode(encoding))
        elif self.ftp_connector_id.type == "sftp":
            with self.get_sftp_connector() as connector:
                f = connector.open(file_path, "r")
                content_str = f.read()
                content = StringIO(unicode(content_str))
        else:
            raise UserError(_("Unknown import type"))

        return content

    @api.model
    def move_file(self, old_path, new_path):
        """
        Move the file from a old path to a new path
        :param old_path: The old path on the source
        :param new_path: The new path on the source
        :return: None
        """
        self.ensure_one()

        if not self.ftp_connector_id:
            shutil.move(old_path, new_path)
        elif self.ftp_connector_id.type == "sftp":
            with self.get_sftp_connector() as connector:
                connector.rename(old_path, new_path)
        else:
            raise UserError(_("Unknown import type"))

    @api.multi
    def put_file(self, current_path, destination_path):
        if not self.ftp_connector_id:
            shutil.move(current_path, destination_path)
        elif self.ftp_connector_id.type == "sftp":
            with self.get_sftp_connector() as connector:
                connector.put(current_path, destination_path)
        else:
            raise UserError(_("Unknown import type"))

    @contextmanager
    def get_sftp_connector(self):
        self.ensure_one()

        if not self.ftp_connector_id:
            raise UserError(_("Please configure a sFTP connector"))

        with self.ftp_connector_id.get_sftp_connector() as connector:
            yield connector

    @contextmanager
    def get_ftp_connector(self):
        self.ensure_one()

        raise NotImplementedError("Please implement this method")


class CSVFileLogger(models.Model):
    _name = "csv.file.logger"
    _order = "create_date DESC"
    _rec_name = "date_start"

    date_start = fields.Datetime("Date start")
    date_end = fields.Datetime("Date end")
    message = fields.Text("Message")
    nbr_lines = fields.Integer("Number of lines")
    duration = fields.Float("Duration")
    state = fields.Selection(
        [("success", "Success"), ("partial", "Partial"), ("error", "Error")],
        default="success",
    )
