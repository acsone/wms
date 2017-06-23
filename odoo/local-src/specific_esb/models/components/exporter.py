# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent, Component

import logging


class ExportMapper(AbstractComponent):
    _name = 'esb.export.mapper'
    _inherit = ['base.export.mapper', 'esb.connector']
    _usage = 'export.mapper'


class ESBExporterMixin(AbstractComponent):

    _name = 'esb.exporter.mixin'
    _inherit = ['base.exporter', 'esb.connector']

    @property
    def logger(self):
        return logging.getLogger(
            '[{}:{}]'.format(self._usage, self.model._name))

    def run(self, items):
        with self.collection.work_on(self.model._name) as work:
            adapter = work.component(usage='xml.write')
            prepared = []
            # TODO: how many items could we have here?
            # Shall we split this in chunks?
            for item in items:
                prepared.append(self.mapper.map_record(item).values())
            path = adapter.write_file(prepared)
            self.logger.info('File created: %s', path)
            return path


class ESBExporter(Component):

    _name = 'esb.exporter'
    _inherit = ['esb.exporter.mixin']
    _usage = 'record.exporter'


class ESBCronExporter(AbstractComponent):

    _name = 'esb.cron.exporter'
    _inherit = ['esb.exporter.mixin']
    _usage = 'record.exporter.cron'

    def get_items_domain(self):
        return []

    def get_items(self):
        return self.model.search(self.get_items_domain())

    def run(self):
        super(ESBCronExporter, self).run(self.get_items())
