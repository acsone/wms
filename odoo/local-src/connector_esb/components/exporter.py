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

    # Set to True if the record must be marked as 'exported'
    # The model must have a 'esb_exported' field
    _mark_as_exported = False

    @property
    def logger(self):
        return logging.getLogger(
            '[{}:{}]'.format(self._usage, self.model._name))

    def _prepare_item(self, items):
        prepared = []
        for item in items:
            prepared.append(self.mapper.map_record(item).values())
        return prepared

    def _export_items(self, items):
        producer = self.work.component(usage='xml.producer')
        writer_type = self.work.timestamp.writer
        assert writer_type
        writer_usage = writer_type + '.xml.writer'
        writer = self.work.component(usage=writer_usage)
<<<<<<< HEAD
        # TODO: how many items could we have here?
        # Shall we split this in chunks?
        prepared = self._prepare_item(items)
        content = producer.produce(prepared)
        path = writer.write_file(content)

        self.logger.info('File created (%s) : %s', writer_type, path)

        if self._mark_as_exported:
            self._mark_items_as_exported(items)
        return path

    def _mark_items_as_exported(self, items):
        """ Mark records as exported

        It updates the fields 'esb_exported' to True on the records
        which have been exported.

        """
        new_exported = self.model.search(
            [('id', 'in', items.ids), ('esb_exported', '=', False)],
        )
        if new_exported:
            self._write_esb_exported_mark_on_records(new_exported)

    def _write_esb_exported_mark_on_records(self, records):
        # we flag the products as exported, bypassing the ORM
        # otherwise the write_date would be modified and the records
        # exported again...
        query = (
            "UPDATE %s SET esb_exported = true "
            "WHERE id IN %%s " % (self.model._table,)
        )
        self.env.cr.execute(query, (tuple(records.ids),))
        self.model.invalidate_cache(
            fnames=['esb_exported'],
            ids=records.ids
        )

    def run(self):
        return NotImplementedError


class ESBExporter(Component):

    _name = 'esb.exporter'
    _inherit = ['esb.exporter.mixin']
    _usage = 'record.exporter'

    def run(self, records):
        return self._export_items(records)


class ESBCronExporter(AbstractComponent):

    _name = 'esb.cron.exporter'
    _inherit = ['esb.exporter.mixin']
    _usage = 'record.exporter.cron'

    def get_items_domain(self):
        return []

    def domain_timestamp(self, export_since=None):
        # write_date is at the very least the same than create_date
        # so we don't need to search on create_date >= self.export_since
        return [('write_date', '>=', export_since)]

    def get_items(self, export_since):
        domain = self.get_items_domain()
        if export_since:
            date_domain = self.domain_timestamp(export_since)
            domain = AND([domain, date_domain])
        return self.model.with_context(active_test=False).search(domain)

    def run(self, export_since=None):
        """ Run the export on a domain

        ``export_since`` can be omitted to ignore the date and export
        all the records that match the domain.

        """
        records = self.get_items(export_since=export_since)
        return self._export_items(records)
