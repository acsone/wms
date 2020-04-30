# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
from contextlib import contextmanager
from functools import partial
from io import StringIO

import dicttoxml
import paramiko
from lxml import etree
from odoo import _, exceptions, fields
from odoo.addons.component.core import AbstractComponent, Component

logging.getLogger('dicttoxml').setLevel(logging.WARN)

SFTP_TIMEOUT = 30

NAMESPACES = (
    # el, ns, attr
    ('Root', 'urn:schemas-microsoft-com:datatypes', 'dt'),
)
for el, ns, attr in NAMESPACES:
    etree.register_namespace(attr, ns)


class ESBXMLProducer(Component):
    """ XML Producer for exports """

    _name = 'esb.xml.producer'
    _inherit = 'esb.base'
    _usage = 'xml.producer'

    namespaces = NAMESPACES
    main_root_el = 'ROOT'
    root_el = 'Root'
    list_item_el = 'Row'

    def _apply_namespaces(self, xml):
        root = etree.XML(xml)
        for el, ns, attr in self.namespaces:
            if len(root.find(el)):
                # NOTE: this sets
                #  `xmlns:dt="urn:schemas-microsoft-com:datatypes"`
                # as well as an empty `dt:dt=""` attribute
                root.find(el).set('{{{}}}{}'.format(ns, attr), '')
        return etree.tostring(
            root, xml_declaration=True, encoding='utf-8', pretty_print=True
        )

    def _produce(self, data, main_root, root):
        # Wrap into root
        if data:
            data = {root: data}
        xml = dicttoxml.dicttoxml(
            data,
            custom_root=main_root,
            attr_type=False,
            item_func=self._dicttoxml_item_func,
        )
        if data:
            xml = self._apply_namespaces(xml)
        # Remove the xml version node
        xml = xml[xml.find('?>') + 2 :]
        return xml

    def _dicttoxml_item_func(self, item):
        return self.list_item_el

    def produce(self, data, main_root='', root=''):
        main_root = main_root or self.main_root_el
        root = root or self.root_el
        return self._produce(data, main_root, root)


class ESBWebServiceXMLProducer(Component):
    """ XML Producer for WebServices """

    _name = 'esb.xml.webservice.producer'
    _inherit = 'esb.base'
    _usage = 'xml.webservice.producer'

    root_el = 'result'
    list_item_el = 'resultItem'

    def _produce(self, data, root, list_item):
        item = partial(self._dicttoxml_item_func, list_item)
        xml = dicttoxml.dicttoxml(
            data, attr_type=False, custom_root=root, item_func=item
        )
        return xml

    def _dicttoxml_item_func(self, list_item, item):
        return list_item

    def produce(self, data, root=None, list_item_el=None):
        root = root or self.root_el
        list_item_el = list_item_el or self.list_item_el
        return self._produce(data, root, list_item_el)


class ESBXMLWriter(AbstractComponent):
    _name = 'esb.xml.writer'
    _inherit = 'esb.base'
    _usage = 'xml.writer'

    @property
    def config(self):
        assert self.work.timestamp, (
            "a esb.backend.timestamp record must " "be passed in work_on"
        )
        return self.work.timestamp

    def filename(self):
        pattern = self.config.export_filename.strip()
        return pattern.format(
            name=self.model._name.replace('.', '_'),
            date=fields.Date.today().replace('-', ''),
            time=fields.Datetime.now().split(' ')[1].replace(':', ''),
        )

    def path(self):
        return self.env.context.get('xml_out_path') or self.config.path or ''

    def write_file(self, content):
        path = self.path()
        filename = self.filename()
        if self._already_exists(path, filename):
            # if we overwrite a file, we might lose data as we are
            # exporting a diff
            raise exceptions.UserError(
                _('File %s already exported.') % (filename,)
            )
        return self._write_file(path, filename, content)

    def _already_exists(path, filename):
        raise NotImplementedError

    def _write_file(self, path, filename, content):
        raise NotImplementedError


class LocalESBXMLWriter(Component):
    _name = 'local.esb.xml.writer'
    _inherit = 'esb.xml.writer'
    _usage = 'local.xml.writer'

    def path(self):
        path = super(LocalESBXMLWriter, self).path()
        if not path:
            path = '/tmp'
        return path

    def write_file(self, content):
        path = self.path()
        filename = self.filename()
        if self._already_exists(path, filename):
            # if we overwrite a file, we might lose data as we are
            # exporting a diff
            raise exceptions.UserError(
                _('File %s already exported.') % (filename,)
            )

        return self._write_file(path, filename, content)

    def _already_exists(self, path, filename):
        return os.path.exists(os.path.join(path, filename))

    def _write_file(self, path, filename, content):
        fullpath = os.path.join(path, filename)
        with open(fullpath, 'w') as thefile:
            thefile.write(content)
        return fullpath


class SFTPESBXMLWriter(Component):
    _name = 'sftp.esb.xml.writer'
    _inherit = 'esb.xml.writer'
    _usage = 'sftp.xml.writer'

    def __init__(self, work_context):
        super(SFTPESBXMLWriter, self).__init__(work_context)
        self._sftp = None

    @contextmanager
    def _sftp_client(self):
        private_key = os.environ.get('ODOO_ESB_SFTP_PRIVATE_KEY')
        assert private_key, "ODOO_ESB_SFTP_PRIVATE_KEY must be set in environ"
        pkey = paramiko.RSAKey.from_private_key(
            StringIO(private_key.decode('utf8'))
        )
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            ssh.connect(
                self.backend_record.sftp_host,
                port=self.backend_record.sftp_port,
                username=self.backend_record.sftp_user,
                pkey=pkey,
                look_for_keys=False,
                timeout=SFTP_TIMEOUT,
            )
            with ssh.open_sftp() as sftp:
                self._sftp = sftp
                yield sftp
        self._sftp = None

    @property
    def sftp(self):
        if self._sftp is None:
            raise ValueError('must be in _sftp_client() context to use sftp')
        return self._sftp

    def path(self):
        """ Construct a path with default sftp path and specific file path """
        file_path = super(SFTPESBXMLWriter, self).path()
        sftp_path = self.backend_record.sftp_path
        if file_path and sftp_path:
            if not sftp_path.endswith('/') and not file_path.startswith('/'):
                return sftp_path + "/" + file_path
        return sftp_path + file_path

    def write_file(self, content):
        with self._sftp_client():
            return super(SFTPESBXMLWriter, self).write_file(content)

    def _already_exists(self, path, filename):
        try:
            self.sftp.stat(os.path.join(path, filename))
        except IOError:
            return False
        return True

    def _write_file(self, path, filename, content):
        # use a tmp file so the esb will not try to read
        # a file during its written
        if path:
            self.sftp.chdir(path)
        tmpfile = filename + '.tmp'
        with self.sftp.open(tmpfile, 'w') as thefile:
            thefile.write(content)
        self.sftp.posix_rename(tmpfile, filename)
        return os.path.join(path, filename)
