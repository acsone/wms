# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import re
from contextlib import contextmanager
from functools import partial
from StringIO import StringIO

import paramiko

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import ConnectorException

_logger = logging.getLogger(__name__)

SFTP_TIMEOUT = 30
BANNER_TIMEOUT = 200


@contextmanager
def open_sftp(paramiko_kwargs):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(**paramiko_kwargs)
        with ssh.open_sftp() as sftp:
            yield sftp


def cleanup_pulled_files(paramiko_kwargs, files_to_remove):
    with open_sftp(paramiko_kwargs) as sftp:
        hostname = paramiko_kwargs["hostname"]
        for file_path in files_to_remove:
            sftp.remove(file_path)
            _logger.debug("SFTP host %s: Removes file %s", hostname, file_path)


class EdiSftpBackendAdapter(Component):

    _name = "edi.sftp.backend.adapter"
    _inherit = "edi.backend.adapter"
    _usage = "sftp.backend.adapter"

    def _get_paramiko_kwarqs(self):
        pk_env_variable = self.backend_record.pk_env_variable
        if not pk_env_variable and not self.backend_record.password:
            raise ConnectorException(
                _("Please set the private key environment variable " "or a password")
            )
        private_key = os.environ.get(pk_env_variable)
        pkey = None
        if pk_env_variable and not private_key:
            raise ConnectorException(_("%s must be set in environ") % pk_env_variable)

        pkey = paramiko.RSAKey.from_private_key(StringIO(private_key.decode("utf8")))
        return dict(
            hostname=self.backend_record.hostname,
            port=self.backend_record.port,
            username=self.backend_record.username,
            password=self.backend_record.password,
            pkey=pkey,
            look_for_keys=False,
            timeout=SFTP_TIMEOUT,
            banner_timeout=BANNER_TIMEOUT,
        )

    @contextmanager
    def open_sftp(self):
        with open_sftp(self._get_paramiko_kwarqs()) as sftp:
            yield sftp

    def push(self, content):
        record = getattr(self.work, "record", None)
        task_def = self.work.task_def
        filename = task_def.filename(record)
        path = os.path.join(task_def.backend_id.path_write or "", task_def.path or "")
        with self.open_sftp() as sftp:
            sftp.chdir(path)
            tmp_filename = filename + ".wip"
            with sftp.open(tmp_filename, "w") as thefile:
                thefile.write(content)
            sftp.rename(tmp_filename, filename)

    def pull(self):
        """
        Return a list of tuple with the content to process.
        The first item into the tuple is a name that could be used to store
        the pulled content into Odoo and the second one is the content.
        """
        task_def = self.work.task_def
        file_pattern = task_def.file_matcher_pattern
        re_pattern = re.compile(file_pattern)
        path = os.path.join(task_def.backend_id.path_read or "", task_def.path or "")
        hostname = self.backend_record.hostname
        result = []
        to_cleanup = []
        with self.open_sftp() as sftp:
            filenames = [f for f in sftp.listdir(path) if re_pattern.match(f)]
            for filename in filenames:
                full_path = os.path.join(path, filename)
                with sftp.file(full_path, "rb") as f:
                    result.append((filename, f.read()))
                _logger.debug("SFTP host %s: Pull file %s", hostname, full_path)
                to_cleanup.append(full_path)

        self.env.cr.after(
            "commit",
            partial(
                cleanup_pulled_files,
                paramiko_kwargs=self._get_paramiko_kwarqs(),
                files_to_remove=to_cleanup,
            ),
        )
        return result

    def test_connection(self):
        with self.open_sftp() as sftp:
            sftp.listdir("/")
