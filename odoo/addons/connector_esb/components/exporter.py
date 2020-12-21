# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging

import psycopg2

import odoo
from odoo import _, fields
from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.connector.exception import RetryableJobError
from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)


class ExportMapper(AbstractComponent):
    _name = "esb.export.mapper"
    _inherit = ["base.export.mapper", "esb.base"]
    _usage = "export.mapper"

    translatable_keys = {
        # 'fr_FR': {
        #     'odoo_field': 'ext_field',
        # }
    }

    def translatable_langs(self):
        return self.env["res.lang"].search([("translatable", "=", True)]).mapped("code")

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
            data = record.source.with_context(lang=lang).read(translatable.keys())[0]
            for fname, extname in translatable.iteritems():
                values[extname] = data[fname]


class ESBWebServiceExporter(AbstractComponent):
    _name = "esb.webservice.exporter"
    _inherit = ["base.exporter", "esb.base"]
    _usage = "record.exporter"

    def __init__(self, working_context):
        super(ESBWebServiceExporter, self).__init__(working_context)
        self.record = None
        self.external_id = None

    def _get_external_id(self):
        """Return the id for the export

        To implement in subclasses. For instance for a sales order, the
        external id is sale.esb_ref.
        """
        raise NotImplementedError

    def run(self, record, *args, **kwargs):
        """Export ``record``

        :param record: record to export

        """
        self.record = record
        self.external_id = self._get_external_id()

        result = self._run(*args, **kwargs)

        # Commit so we keep the external ID when we do something in
        # _after_export and it fails. The commit will also release the lock
        # acquired on the record
        if not odoo.tools.config["test_enable"]:
            self.env.cr.commit()  # noqa

        self._after_export()
        return result

    def _run(self):
        """Flow of the synchronization, implemented in inherited classes"""
        assert self.record

        if self._has_to_skip():
            return

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        map_record = self._map_data()

        if self.external_id:
            record = self._update_data(map_record)
            if not record:
                return _("Nothing to export.")
            self._update(record)
        else:
            record = self._create_data(map_record)
            if not record:
                return _("Nothing to export.")
            result = self._create(record)
            self._postprocess_create_result(result)
        return _("Record exported")

    def _postprocess_create_result(self, result):
        raise NotImplementedError

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~odoo.addons.connector.components.mapper.MapRecord`
        """
        return self.mapper.map_record(self.record)

    def _create_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_create` """
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """ Create the External record """
        return self.backend_adapter.create(data)

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        return map_record.values(fields=fields, **kwargs)

    def _update(self, data):
        """ Update an External record """
        assert self.external_id
        self.backend_adapter.write(self.external_id, data)

    def _after_export(self):
        """Can do several actions after exporting a record on the backend"""
        pass

    def _lock(self, records=None):
        """Lock the record.

        Lock the record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.
        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.
        """
        if not records and not self.record:
            return
        sql = "SELECT id FROM %s WHERE ID in %%s FOR UPDATE NOWAIT" % self.model._table
        record_ids = tuple(records.ids) if records else (self.record.id,)
        try:
            self.env.cr.execute(sql, (record_ids,), log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info(
                "A concurrent job is already exporting the same "
                "record (%s with id %s). Job delayed later.",
                self.model._name,
                record_ids,
            )
            raise RetryableJobError(
                "A concurrent job is already exporting the same record "
                "(%s with id %s). The job will be retried later."
                % (self.model._name, record_ids)
            )

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        # this variable contains the name of the models
        # that _inherit from 'esb.exportable'
        exportable_models = self.env["esb.exportable"]._inherit_children
        # The 'esb.exportable' abstract model implements an
        # 'esb_is_exportable' method. Use it when available.
        if self.model._name in exportable_models:
            return not self.record.esb_is_exportable()
        return False


class ESBExporterMixin(AbstractComponent):

    _name = "esb.exporter.mixin"
    _inherit = ["base.exporter", "esb.base"]

    # Set to True if the record must be marked as 'exported'
    # The model must have a 'esb_exported' field
    _mark_as_exported = False

    @property
    def logger(self):
        return logging.getLogger(u"[{}:{}]".format(self._usage, self.model._name))

    def _prepare_item(self, items):
        prepared = []
        for item in items:
            prepared.append(self.mapper.map_record(item).values())
        return prepared

    def _get_producer(self):
        return self.work.component(usage="xml.producer")

    def _export_items(self, items):
        producer = self._get_producer()
        writer_type = self.work.timestamp.writer
        assert writer_type
        writer_usage = writer_type + ".xml.writer"
        writer = self.work.component(usage=writer_usage)
        # TODO: how many items could we have here?
        # Shall we split this in chunks?
        prepared = self._prepare_item(items)
        content = producer.produce(prepared)
        path = writer.write_file(content)

        self.logger.info("File created (%s) : %s", writer_type, path)

        if self._mark_as_exported:
            self._mark_items_as_exported(items)
        return path

    def _mark_items_as_exported(self, items):
        """ Mark records as exported

        It updates the fields 'esb_exported' to True on the records
        which have been exported.

        """
        new_exported = self.model.search(
            [("id", "in", items.ids), ("esb_exported", "=", False)]
        )
        if new_exported:
            self._write_esb_exported_mark_on_records(new_exported)

    def _write_esb_exported_mark_on_records(self, records):
        # we flag the products as exported, bypassing the ORM
        # otherwise the write_date would be modified and the records
        # exported again...
        query = "UPDATE %s SET esb_exported = true " "WHERE id IN %%s " % (
            self.model._table,
        )
        self.env.cr.execute(query, (tuple(records.ids),))
        self.model.invalidate_cache(fnames=["esb_exported"], ids=records.ids)

    def _lock(self, records):
        """Lock the records.

        Records being modified in a transaction starting before an export and
        finishing after; may not be picked up by the next export as their
        write_date (start time of the transaction) would be anterior to the
        timestamp last export.

        """
        if not records:
            return
        sql = "SELECT id FROM %s WHERE id in %%s FOR UPDATE NOWAIT" % self.model._table
        try:
            self.env.cr.execute(sql, (tuple(records.ids),), log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info(
                "The export on (%s with ids %s) could not be done."
                "some locked records prevented the execution.",
                self.model._name,
                records.ids,
            )
            raise RetryableJobError(
                "Concurrent access prevented the job to export the records "
                "(%s with id %s). The job will be retried later."
                % (self.model._name, records.ids)
            )

    def run(self):
        return NotImplementedError


class ESBExporter(Component):

    _name = "esb.exporter"
    _inherit = ["esb.exporter.mixin"]
    _usage = "record.exporter"

    def run(self, records):
        return self._export_items(records)


class ESBCronExporter(AbstractComponent):

    _name = "esb.cron.exporter"
    _inherit = ["esb.exporter.mixin"]
    _usage = "record.exporter.cron"

    BASIC_LOCK_TIME = 60

    def get_items_domain(self):
        return []

    def domain_timestamp(self, export_since=None, export_to=None):
        """ Create a search domain for a timestamp

        To export only the changes since last export
        As write_date is at the very least the same than create_date
        no need to search on create_date >= self.export_since.

        To be sure that we don't miss a record that is updated during
        the last export a few seconds are subtracted from the timestamp.
        Yes poor man locking system !
        But the FOR UPDATE NO WAIT did not seem to succeed at all on the
        product.product table when addressing many records.
        """
        domain = []
        if export_since:
            export_date = fields.Datetime.from_string(export_since)
            export_date = export_date - datetime.timedelta(seconds=self.BASIC_LOCK_TIME)
            export_since = fields.Datetime.to_string(export_date)
            domain.append(("write_date", ">=", export_since))
        if export_to:
            export_date = fields.Datetime.from_string(export_to)
            export_date = export_date + datetime.timedelta(seconds=self.BASIC_LOCK_TIME)
            export_since = fields.Datetime.to_string(export_date)
            domain.append(("write_date", "<=", export_since))
        return domain

    def get_items(self, export_since, export_to=None):
        domain = self.get_items_domain()
        if export_since:
            date_domain = self.domain_timestamp(export_since, export_to=export_to)
            domain = AND([domain, date_domain])
        items = self.model.with_context(active_test=False).search(domain)
        return items

    def run(self, export_since=None, export_to=None, max_records=0):
        """ Run the export on a domain

        ``export_since`` can be omitted to ignore the date and export
                         all the records that match the domain.
        ``export_to`` can be omitted to ignore the date and export
                      all the records that match the domain.
        ``max_records``  the maximum number of records that must be exported
                         in one export. Can be ommited to export all records
                         that need exporting. (Only used by cron web service
                         export)
        ``return``       the path of the file exported
        """
        records = self.get_items(export_since=export_since, export_to=export_to)
        return self._export_items(records)


class ESBWebServiceCronExporter(AbstractComponent):
    _name = "esb.webservice.cron.exporter"
    _inherit = ["esb.webservice.exporter", "esb.cron.exporter"]
    _usage = "record.exporter.cron"

    def run(self, export_since=None, max_records=0):
        """ Run the export on a domain

        ``export_since`` can be omitted to ignore the date and export
                         all the records that match the domain.
        ``max_records``  the maximum number of records that must be exported
                         in one export. Can be ommited to export all records
                         that need exporting.
        ``return``       the datetime of the last write_date exported, but
                         only if there was more than max_records to export.

        """
        records = self.get_items(export_since=export_since)
        data = []
        for r in records:
            mapped_record = self.mapper.map_record(r)
            data.append(self._update_data(mapped_record))
        if data:
            data = {"lines": data}
            self._create(data)
        return
