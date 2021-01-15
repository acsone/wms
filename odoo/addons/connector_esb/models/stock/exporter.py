# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from datetime import timedelta

from odoo import fields
from odoo.osv.expression import AND

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import ConnectorException

from ...components.mapper import falsy2emptystring, falsy2zero

_logger = logging.getLogger(__name__)


class StockUpdateMapper(Component):
    _name = "esb.stock.update.export.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "product.product"

    @classmethod
    def _component_match(cls, work):
        return bool(
            work.timestamp
            and work.timestamp.kind in ["stock.update", "stock.update.single"]
        )

    direct = [
        (falsy2emptystring("default_code"), "sku"),
        (falsy2zero("immediately_usable_qty"), "qty"),
    ]

    @mapping
    def compute_erpstockcode(self, record):
        value = ""
        if record.product_tmpl_id.state_id:
            value = record.product_tmpl_id.state_id.esb_ref or ""
        return {"erp_stock_code": value}

    @mapping
    def compute_date_peremption(self, record):
        """Get the closest (to now) expiration date."""
        value = record.older_lot_id.life_date or ""
        return {"date_peremption": value[:10]}

    @mapping
    def compute_sales_average(self, record):
        """ Compute the daily average quantity of sale on a year

        Using direct sql to speed up the export.
        """
        sql = """
            SELECT
                COALESCE(SUM(sol.product_uom_qty), 0) /365
            FROM sale_order_line AS sol
            LEFT JOIN sale_order AS so ON sol.order_id = so.id
            WHERE sol.state not in ('cancel')
                  AND so.date_order > current_date - interval '1' year
                  AND sol.product_id = %s
        """
        self.env.cr.execute(sql, [record.id])
        sale_average = self.env.cr.fetchone()[0]
        return {"sales_average": round(sale_average or 0, 1)}


class StockUpdateExporter(Component):
    """Multiple product stock status exporter, scheduled by cron."""

    _name = "esb.stock.update.webservice.exporter"
    _inherit = "esb.webservice.cron.exporter"
    _apply_on = "product.product"
    _base_backend_adapter_usage = "backend.adapter.stockupdate"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "stock.update")

    def get_items(self, export_since, export_to=None):
        """Find all quants that need to be exported.

        Returns the quants instead of the products directly because the
        write_date on the quants is used to manage the maximum of records
        that can be sent.
        """
        domain = [
            ("product_id.default_code", "!=", ""),
            ("product_id.default_code", "!=", False),
            ("product_id.type", "=", "product"),
            ("product_id.sale_ok", "=", True),
        ]
        if export_since:
            date_domain = self.domain_timestamp(export_since, export_to=export_to)
            domain = AND([domain, date_domain])
        StockMove = self.env["stock.quant"]
        # uses auto_join on stock_moveto avoid that the orm do a first
        # query to get all the product's ids
        # and uses a "product_id in" operator into the final query
        with StockMove._auto_join(["product_id"]):
            return StockMove.search(domain, order="write_date asc")

    @classmethod
    def get_exported_until(cls, last_export):
        """ Make a timestamp based on what has been exported.

        If some records have been exported, but not all. Thes a corresponding
        timestamp is created taking into account the basic lock offset.
        Note that the last second will be re-exported.
        """
        return fields.Datetime.to_string(
            fields.Datetime.from_string(last_export)
            + timedelta(seconds=cls.BASIC_LOCK_TIME)
        )

    def run(self, export_since=None, export_to=None, max_records=0):
        """ Run the export of multiple stock status.

        ``export_since`` can be omitted to ignore the date and export
        all the records that match the domain.
        ``max_records`` can be set to export only a maximum number of records
        """

        data = []
        exported_ids = []
        last_export = None
        quants = self.get_items(export_since=export_since, export_to=export_to)
        for quant in quants:
            if quant.product_id.id not in exported_ids:
                mapped_record = self.mapper.map_record(quant.product_id)
                data.append(self._update_data(mapped_record))
                exported_ids += [quant.product_id.id]
                if max_records != 0 and len(exported_ids) >= max_records:
                    # Export a batch of product state
                    try:
                        self._create({"lines": data})
                        _logger.debug("Stock_exported_until %s", quant.write_date)
                    except ConnectorException:
                        if last_export:
                            return self.get_exported_until(last_export)
                        raise  # No succesful export, job failed
                    else:
                        last_export = quant.write_date
                        _logger.debug("Exporting stock status : %s", data)
                    exported_ids = []
                    data = []
        if data:
            try:
                self._create({"lines": data})
            except ConnectorException:
                if last_export:
                    return self.get_exported_until(last_export)
                raise  # No succesful export, job failed
        return


class StockUpdateServiceExporter(Component):
    """Single product stock status exporter."""

    _name = "esb.stock.update.webservice.exporter.single"
    _inherit = "esb.webservice.exporter"
    _apply_on = "product.product"
    _base_backend_adapter_usage = "backend.adapter.stockupdate"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "stock.update.single")

    def _get_external_id(self):
        """Always send a POST request, so no external id."""
        return None

    def _postprocess_create_result(self, result):
        return
