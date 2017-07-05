# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv.expression import AND
from odoo.addons.component.core import AbstractComponent, Component

import logging


class ExportMapper(AbstractComponent):
    _name = 'esb.export.mapper'
    _inherit = ['base.export.mapper', 'esb.base']
    _usage = 'export.mapper'

    translatable_keys = {
        # 'fr_FR': {
        #     'odoo_field': 'ext_field',
        # }
    }

    def translatable_langs(self):
        return self.env['res.lang'].search([
            ('translatable', '=', True)]).mapped('code')

    def finalize(self, record, values):
        values = super(ExportMapper, self).finalize(record, values)
        self.handle_translations(record, values)
        return values

    def handle_translations(self, record, values):
        """Collect and translate fields to be translated."""
        for lang in self.translatable_langs():
            if lang not in self.translatable_keys:
                continue
            translatable = self.translatable_keys[lang]
            data = record.source.with_context(
                lang=lang).read(translatable.keys())[0]
            for fname, extname in translatable.iteritems():
                values[extname] = data[fname]


class ESBExporterMixin(AbstractComponent):

    _name = 'esb.exporter.mixin'
    _inherit = ['base.exporter', 'esb.base']

    @property
    def logger(self):
        return logging.getLogger(
            '[{}:{}]'.format(self._usage, self.model._name))

    def run(self, items):
        producer = self.work.component(usage='xml.producer')
        writer = self.work.component(usage='xml.writer')
        prepared = []
        # TODO: how many items could we have here?
        # Shall we split this in chunks?
        for item in items:
            prepared.append(self.mapper.map_record(item).values())
        content = producer.produce(prepared)
        path = writer.write_file(content)
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

    def get_items(self, export_since=None):
        domain = self.get_items_domain()
        if export_since:
            # write_date is at the very least the same than create_date
            # so we don't need to search on create_date >= self.export_since
            date_domain = [('write_date', '>=', export_since)]
            domain = AND([domain, date_domain])
        return self.model.with_context(active_test=False).search(domain)

    def run(self, export_since=None):
        """ Run the export on a domain

        ``export_since`` can be omitted to ignore the date and export
        all the records that match the domain.

        """
        records = self.get_items(export_since=export_since)
        return super(ESBCronExporter, self).run(records)
