# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os

from lxml import etree

import dicttoxml

from odoo import fields
from odoo.addons.component.core import Component

logging.getLogger('dicttoxml').setLevel(logging.WARN)

NAMESPACES = (
    # el, ns, attr
    ('Root', 'urn:schemas-microsoft-com:datatypes', 'dt'),
)
for el, ns, attr in NAMESPACES:
    etree.register_namespace(attr, ns)


class ESBXMLProducer(Component):
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
                root.find(el).set('{%s}%s' % (ns, attr), '')
        return etree.tostring(
            root, xml_declaration=True,
            encoding='utf-8', pretty_print=True)

    def _produce(self, data, main_root, root):
        # wrap into root
        data = {root: data}
        xml = dicttoxml.dicttoxml(
            data, custom_root=main_root,
            attr_type=0, item_func=self._dicttoxml_item_func)
        xml = self._apply_namespaces(xml)
        return xml

    def _dicttoxml_item_func(self, item):
        return self.list_item_el

    def produce(self, data, main_root='', root=''):
        main_root = main_root or self.main_root_el
        root = root or self.root_el
        return self._produce(data, main_root, root)


class ESBXMLWriterWriter(Component):
    _name = 'esb.adapter.xml.writer'
    _inherit = 'esb.base'
    _usage = 'xml.writer'

    def filename(self):
        timestamp = self.env['esb.backend.timestamp'].search(
            [('backend_id', '=', self.backend_record.id),
             ('model', '=', self.work.model_name),
             ('kind', '=', self.work.kind),
             ]
        )
        pattern = timestamp.export_filename
        return pattern.format(
            name=self.model._name.replace('.', '_'),
            date=fields.Date.today().replace('-', ''))

    def path(self):
        return (self.env.context.get('xml_out_path') or
                self.collection.sftp_location or '/tmp')

    def write_file(self, content):
        fullpath = os.path.join(self.path(), self.filename())
        self._write_file(fullpath, content)
        return fullpath

    def _write_file(self, path, content):
        with open(path, 'w') as thefile:
            thefile.write(content)
