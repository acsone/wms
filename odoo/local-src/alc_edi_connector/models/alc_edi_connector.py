# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import os
from contextlib import contextmanager
from datetime import datetime
from StringIO import StringIO

import paramiko
from odoo import _, api, fields, models
from odoo.exceptions import UserError

SFTP_TIMEOUT = 30


class AlcEdiConnector(models.Model):

    _name = 'alc.edi.connector'
    _description = 'Edi Connector'

    name = fields.Char(required=True)
    channel = fields.Selection(
        [('sftp', 'ftp/sftp')], required=True, default="sftp"
    )
    hostname = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char()
    port = fields.Integer(default=22)
    pk_env_variable = fields.Char(
        'Private key environment variable',
        help='The name of the environment variable who '
        'contains the private sh key',
    )
    path_read = fields.Char()
    path_write = fields.Char()

    @contextmanager
    def open_sftp(self):
        self.ensure_one()

        pk_env_variable = self.pk_env_variable
        if not pk_env_variable or not self.password:
            raise UserError(
                _(
                    'Please set the private key environment variable '
                    'or a password'
                )
            )
        private_key = os.environ.get(pk_env_variable)
        pkey = None
        if pk_env_variable and not private_key:
            raise UserError(_('%s must be set in environ') % pk_env_variable)

            pkey = paramiko.RSAKey.from_private_key(
                StringIO(private_key.decode('utf8'))
            )

        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            ssh.connect(
                self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                pkey=pkey,
                look_for_keys=False,
                timeout=SFTP_TIMEOUT,
            )
            with ssh.open_sftp() as sftp:
                yield sftp

    @api.multi
    def test_connection(self):
        self.ensure_one()

        if self.type == 'sftp':
            self.test_sftp_connection()

    @api.multi
    def test_sftp_connection(self):
        self.ensure_one()

        with self.get_sftp_connector() as connector:
            connector.listdir('/')

        raise UserError(_('Everything seems ok'))

    def send_order_document(self, purchase_order):
        self.ensure_one()
        xml_content = purchase_order.generate_ubl_xml_string(
            "order", version="2.2"
        )
        filename = "{po_id}_{dt}.xml".format(
            po_id=purchase_order.id, dt=fields.Datetime.now()
        )
        tmp_filename = filename + ".tmp"
        filepath = os.path.join(self.path_write, filename)
        tmp_filepath = os.path.join(self.path_write, tmp_filename)
        with self.open_sftp() as sftp:
            with sftp.open(tmp_filepath, "w") as f:
                f.write(xml_content)
            sftp.rename(tmp_filepath, filepath)
        attachment_name = (
            "UblOrderDocument_%s.xml"
            % fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self, datetime.now())
            )
        )
        self.env['ir.attachment'].create(
            {
                'name': attachment_name,
                'res_id': purchase_order.id,
                'res_model': purchase_order._name,
                'datas': base64.b64encode(xml_content),
                'datas_fname': attachment_name,
            }
        )
