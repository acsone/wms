# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import ConnectorException

from ...components.mapper import falsy2emptystring, falsy2zero

_logger = logging.getLogger(__name__)


class SaleExportMapper(Component):
    _name = "esb.sale.order.export.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "sale.order"

    direct = [
        ("id", "erp_id"),
        (falsy2emptystring("name"), "erp_name"),
        (falsy2zero("amount_total"), "order_amount"),
        (falsy2zero("delivery_price"), "shipping_amount"),
    ]

    children = [("order_line", "lines", "sale.order.line")]

    @mapping
    def compute_customer_esbref(self, record):
        return {"customer_id": record.partner_id.ref or ""}

    @mapping
    def compute_date(self, record):
        return {"date": record.date_order[:10]}

    @mapping
    def compute_serial_no(self, record):
        """It's a char field in odoo and web service wants an int"""
        if record.suite_name:
            try:
                value = int(record.suite_name)
            except ValueError:
                return {}
            return {"serial_no": value}
        return {}

    @mapping
    def compute_channel(self, record):
        # Phone channel '01' is the default
        if record.sale_channel in ("phone", "newpharma"):
            channel = "01"
        elif record.sale_channel == "fax":
            channel = "03"
        elif record.sale_channel == "mail":
            channel = "08"
        elif record.sale_channel == "web":
            channel = "04"
        else:
            raise ConnectorException(
                "Incorrect or empty sale channel {}.".format(record.sale_channel)
            )
        return {"channel": channel}

    @mapping
    def compute_shipping_method(self, record):
        return {
            "shipping_method": record.carrier_id.esb_ref
            or self.env.ref("__setup__.deliver_carrier_alcyon").esb_ref
        }

    @mapping
    def compute_order_ref(self, record):
        if record.client_order_ref:
            return {"order_ref": record.client_order_ref or ""}
        return {}

    @mapping
    def compute_status(self, record):
        status = ""
        if record.state == "cancel":
            status = "canceled"
        elif record.state in ["draft", "sale", "sent", "confirm_background"]:
            status = "processing"
            partial = record.order_line.filtered(lambda r: r.qty_delivered > 0)
            if len(partial) > 0:
                status = "partially_shipped"
        elif record.state == "done":
            status = "complete"
        return {"status": status}

    @mapping
    def compute_taxe_amounts(self, record):
        """Compute the taxes existing on the sale order.

        The apb tax needs to be separated from the other ones. It is a fixed
        amount calculated on the quantity of a product.
        And needs to be subtracted from the total of taxes
        """
        apb_tax = self.env.ref("l10n_be_apb_tax.1_apb_01_out")
        total_amount = record.amount_tax or 0
        lines_with_apb = record.mapped("order_line").filtered(
            lambda r: apb_tax in r.product_id.taxes_id
        )
        total_apb = round(
            sum(lines_with_apb.mapped(lambda r: r.product_uom_qty * apb_tax.amount)), 2
        )
        total_amount = round(total_amount, 2) - total_apb
        return {
            "apb_tax_amount": total_apb,
            "tax_amount": total_amount if total_amount > 0 else 0,
        }

    @mapping
    def compute_increment_id(self, record):
        """ If an esb_ref exists, it is an update, so lets add it """
        if record.esb_ref:
            return {"increment_id": record.esb_ref or ""}


class SaleWebServiceExporter(Component):

    _name = "esb.sale.order.webservice.exporter"
    _inherit = "esb.webservice.exporter"
    _apply_on = "sale.order"
    _base_backend_adapter_usage = "backend.adapter.saleorder"

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        if super(SaleWebServiceExporter, self)._has_to_skip():
            return True
        # we don't care about sales without lines, they are
        # not accepted by the ESB anyway
        if not self.record.order_line:
            return True
        if not self.record.partner_id.email:
            return True
        return False

    def _get_external_id(self):
        """Return the id for the export

        To implement in subclasses. For instance for a sales order, the
        external id is sale.esb_ref.
        """
        return self.record.esb_ref

    def _postprocess_create_result(self, result):
        """Write locally the ids of the export record

        The response of the ESB webservice should be:

         {"erp_id": "42",
          "increment_id": "1000000348",
          "lines": [
              {"line_number": 10 , "created_id": 106},
              {"line_number": 20 , "created_id": 107},
          ]
         }

        """
        _logger.info("result from HTTP POST request %s", result)
        external_id = result["increment_id"]
        self.record.with_context(no_connector_export=True).write(
            {"esb_ref": external_id}
        )
        # Fix, their web service does not send one line in an array
        lines = result["lines"]
        if not isinstance(lines, list):
            lines = [lines]

        for sol in self.record["order_line"]:
            # find the id that matches the line we created
            # on Magento so we can set the corresponding esb_ref
            line = next((line for line in lines if line["line_number"] == sol.id), "")
            if line:
                sol.with_context(no_connector_export=True).write(
                    {"esb_ref": line["created_id"]}
                )
