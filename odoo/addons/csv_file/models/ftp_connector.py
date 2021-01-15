# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
from contextlib import contextmanager
from ftplib import FTP
from io import StringIO

import paramiko

from odoo import _, api, fields, models
from odoo.exceptions import UserError

SFTP_TIMEOUT = 30


class FTPConnector(models.Model):
    _name = "ftp.connector"

    name = fields.Char(required=True)
    type = fields.Selection(
        [("ftp", "FTP"), ("sftp", "sFTP")], string="Type", required=True
    )
    hostname = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char()
    port = fields.Integer(default=22)
    pk_env_variable = fields.Char(
        "Primary key environment variable",
        help="The name of the environment variable who " "contains the primary key",
    )

    def get_ftp_connector(self):
        self.ensure_one()

        return FTP(self.hostname, self.username, self.password)

    @contextmanager
    def get_sftp_connector(self):
        self.ensure_one()

        pk_env_variable = self.pk_env_variable
        if not pk_env_variable:
            raise UserError(_("Please set the primary key environment variable"))

        private_key = os.environ.get(pk_env_variable)
        if not private_key:
            raise UserError(_("%s must be set in environ") % pk_env_variable)

        pkey = paramiko.RSAKey.from_private_key(StringIO(private_key.decode("utf8")))

        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            ssh.connect(
                self.hostname,
                port=self.port,
                username=self.username,
                pkey=pkey,
                look_for_keys=False,
                timeout=SFTP_TIMEOUT,
            )
            with ssh.open_sftp() as sftp:
                yield sftp

    @api.multi
    def test_connection(self):
        self.ensure_one()

        if self.type == "sftp":
            self.test_sftp_connection()
        else:
            self.test_ftp_connection()

    @api.multi
    def test_ftp_connection(self):
        self.ensure_one()

        with self.get_ftp_connector() as connector:
            connector.dir("/")

        raise UserError(_("Everything seems ok"))

    @api.multi
    def test_sftp_connection(self):
        self.ensure_one()

        with self.get_sftp_connector() as connector:
            connector.listdir("/")

        raise UserError(_("Everything seems ok"))
