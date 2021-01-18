# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

import mock
import requests

from odoo.tests.common import SavepointCase

from odoo.addons.connector.exception import ConnectorException


def put_ret_status(url, data, headers, auth):
    resp = requests.Response()
    resp.status_code = 200
    resp.json = lambda: {"erp_id": "42", "increment_id": "1000000348"}
    return resp


def post_ret_status(url, data, headers, auth):
    resp = requests.Response()
    resp.status_code = 200
    resp.json = lambda: {
        "erp_id": "42",
        "increment_id": "1000000348",
        "lines": [{"line_number": 10, "created_id": 106}],
    }
    return resp


class ExportSaleOrderTestCase(SavepointCase):

    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super(ExportSaleOrderTestCase, cls).setUpClass()

        os.environ["ODOO_ESB_WS_USER"] = "ws_user"
        os.environ["ODOO_ESB_WS_BASE_URL"] = "https://test.com"
        os.environ["ODOO_ESB_WS_PWD"] = "pwd"

        cls.backend_model = cls.env["esb.backend"]
        cls.backend = cls.backend_model.get_singleton()

        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.ref = "123321"
        cls.partner_newpharma = cls.env["res.partner"].create(
            {
                "name": "newpharam",
                "ref": cls.env["res.partner"].newpharma_refs[0],
                "email": "newpharma@test.be",
            }
        )
        cls.prod1 = cls.env.ref("product.product_product_1")
        cls.prod2 = cls.env.ref("product.product_product_2")
        cls.model = cls.env["sale.order"]
        cls.setup_records()

    @classmethod
    def setup_records(cls):
        cls.delivery = cls.env["delivery.carrier"].search(
            [("free_if_more_than", "=", False)], limit=1
        )
        cls.delivery.esb_ref = "03"
        cls.prod1.default_code = "SKU01"
        cls.prod1.default_code = "SKU02"
        # Create the abp tax and it's corresponding xmlid on account.tax
        # As the l10n_be module installs it in account_tax_template
        # And it is created in account.tax by the chart of account module
        cls.apb_tax = cls.env["account.tax"].create(
            {
                "description": "APB-OUT",
                "company_id": 1,
                "include_base_amount": False,
                "analytic": False,
                "tax_adjustment": False,
                "type_tax_use": "sale",
                "active": True,
                "name": "APB Out",
                "amount": 0.0224,
            }
        )
        cls.env["ir.model.data"].create(
            {
                "module": "l10n_be_apb_tax",
                "name": "1_apb_01_out",
                "model": "account.tax",
                "res_id": cls.apb_tax.id,
            }
        )
        # And also add a vat tax of 6%
        cls.vat_tax = cls.env["account.tax"].create(
            {
                "description": "6percent",
                "company_id": 1,
                "include_base_amount": False,
                "analytic": False,
                "tax_adjustment": False,
                "type_tax_use": "sale",
                "active": True,
                "name": "6percent",
                "amount_type": "percent",
                "amount": 6.0000,
            }
        )
        cls.prod1.taxes_id = [(4, cls.apb_tax.id, False), (4, cls.vat_tax.id, False)]
        cls.so1 = cls.model.create(
            {
                "esb_ref": "ref_01",
                "partner_id": cls.partner.id,
                "date_order": "2018-01-29",
                "sale_channel": "fax",
                "carrier_id": cls.delivery.id,
                "client_order_ref": "whatever the client want",
                "delivery_price": 23.5,
                "suite_name": "0123434234",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": cls.prod1.name,
                            "product_id": cls.prod1.id,
                            "product_uom_qty": 7,
                        },
                    )
                ],
            }
        )
        cls.so2 = cls.model.create(
            {
                "esb_ref": "ref_02",
                "partner_id": cls.partner.id,
                "date_order": "2018-01-29",
                "sale_channel": "phone",
                "carrier_id": cls.delivery.id,
                "client_order_ref": "whatever the client want",
                "delivery_price": 23.5,
                "suite_name": "0123434234",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": cls.prod1.name,
                            "product_id": cls.prod1.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        cls.so_newpharma = cls.model.create(
            {
                "partner_id": cls.partner_newpharma.id,
                "date_order": "2018-01-29",
                "sale_channel": "newpharma",
                "carrier_id": cls.delivery.id,
                "client_order_ref": "whatever the client want",
                "delivery_price": 23.5,
                "suite_name": "0123434234",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": cls.prod1.name,
                            "product_id": cls.prod1.id,
                            "product_uom_qty": 7,
                        },
                    )
                ],
            }
        )

    def test_mapper_01(self):
        """ Generate data dict with mapper and check with what is expected """
        so = self.so1
        expected = {
            "erp_id": so.id,
            "erp_name": so.name,
            "customer_id": so.partner_id.ref,
            "date": so.date_order.split(" ")[0],
            "channel": "03",  # the code for fax
            "order_ref": so.client_order_ref,
            "status": "processing",
            "shipping_method": so.carrier_id.esb_ref,
            "apb_tax_amount": 0.16,
            "order_amount": so.amount_total,
            "tax_amount": round(so.amount_tax - 0.1568, 2),
            "shipping_amount": so.delivery_price,
            "serial_no": int(so.suite_name),
            "increment_id": so.esb_ref,
            "lines": [
                {
                    "line_number": so.order_line[0].esb_ref,
                    "price": so.order_line[0].price_unit,
                    "price_inc_tax": round(
                        so.order_line[0].price_unit
                        + so.order_line[0].price_reduce_taxinc
                        - so.order_line[0].price_reduce,
                        2,
                    ),
                    "qty_ordered": so.order_line[0].product_uom_qty,
                    "qty_delivered": so.order_line[0].qty_delivered,
                    "qty_cancelled": so.order_line[0].product_qty_canceled,
                    "qty_backorder": so.order_line[0].product_qty_unavailable,
                    "sku": so.order_line[0].product_id.default_code,
                }
            ],
        }
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(so).values()
        self.maxDiff = None
        self.assertDictEqual(values, expected)

    def test_mapper_02(self):
        """Test default values."""
        so = self.so2
        expected = {
            "erp_id": so.id,
            "erp_name": so.name,
            "customer_id": so.partner_id.ref,
            "date": so.date_order.split(" ")[0],
            "channel": "01",
            "order_ref": so.client_order_ref,
            "status": "processing",
            "shipping_method": so.carrier_id.esb_ref,
            "apb_tax_amount": 0.02,
            "order_amount": so.amount_total,
            "tax_amount": round(so.amount_tax - 0.02, 2),
            "shipping_amount": so.delivery_price,
            "serial_no": int(so.suite_name),
            "increment_id": so.esb_ref,
            "lines": [
                {
                    "line_number": so.order_line[0].esb_ref,
                    "price": so.order_line[0].price_unit,
                    "price_inc_tax": round(
                        so.order_line[0].price_unit
                        + so.order_line[0].price_reduce_taxinc
                        - so.order_line[0].price_reduce,
                        2,
                    ),
                    "qty_ordered": so.order_line[0].product_uom_qty,
                    "qty_delivered": so.order_line[0].qty_delivered,
                    "qty_cancelled": so.order_line[0].product_qty_canceled,
                    "qty_backorder": so.order_line[0].product_qty_unavailable,
                    "sku": so.order_line[0].product_id.default_code,
                }
            ],
        }
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(so).values()
        self.maxDiff = None
        self.assertDictEqual(values, expected)

    def test_mapper_sale_channel_incorrect(self):
        """Check empty incorrect sale_channel.

        If the sale_channel is empty or of unknown value the job must fail.
        """
        so = self.so2
        so.sale_channel = ""
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage="export.mapper")
            with self.assertRaises(ConnectorException):
                mapper.map_record(so).values()

    def test_order_line_is_delivery_not_exported(self):
        """Check sale order line with is_delivery set to True.

        Sale order line that contains information about the delivery method
        should not be exported.
        """
        so = self.so2
        so.order_line[0].is_delivery = True
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(so).values()
        self.assertEqual(len(values["lines"]), 0)

    def test_correct_postprocess(self):
        """ Test sale order is updated correctely with return values """
        with self.backend.work_on(self.model._name) as work:
            exporter = work.component(usage="record.exporter")
            exporter.record = self.so1
            result = {
                "erp_id": "42",
                "increment_id": "1000000348",
                "lines": [
                    {"line_number": self.so1.order_line[0].id, "created_id": 106}
                ],
            }
            exporter._postprocess_create_result(result)
        self.assertEqual(self.so1.esb_ref, result["increment_id"])
        self.assertEqual(
            self.so1.order_line[0].esb_ref, result["lines"][0]["created_id"]
        )

    @mock.patch("requests.put", side_effect=put_ret_status)
    def test_record_exporter(self, put):
        """Test export of a sale order catching the put request."""
        self.so1.action_confirm()
        with self.backend.work_on(self.model._name) as work:
            exporter = work.component(usage="record.exporter")
            exporter.run(self.so1)
        put.assert_called_once()

    @mock.patch("requests.post", side_effect=post_ret_status)
    def test_record_exporter_new_pharam(self, post):
        """Test export of a sale order catching the put request."""
        self.so_newpharma.action_confirm()
        with self.backend.work_on(self.model._name) as work:
            exporter = work.component(usage="record.exporter")
            exporter.run(self.so_newpharma)
        post.assert_called_once()
        self.assertEqual(self.so_newpharma.esb_ref, "1000000348")

    def test_mapper_state_in_confirm_background(self):
        """ Check status sent for sale order being confirmed in background."""
        so = self.so1
        so.state = "confirm_background"
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(so).values()
        self.assertEqual(values["status"], "processing")

    def test_so_exported_when_qty_canceled(self):
        """Check sale order is exported when a quantity canceled is changed."""
        self.so1.action_confirm()
        self.so1.state = "sale"
        # Clear the context from _sale_order_create left over from creation
        self.so1.order_line[0].env.context = {}
        with mock.patch(
            "odoo.addons.queue_job.models.base.DelayableRecordset"
        ) as export_record:
            self.so1.order_line[0].write({"product_qty_canceled": 1})
            self.assertEqual(export_record.call_count, 1)

    def test_mapper_when_qty_canceled(self):
        """
        Data:
            A sale order with a line with qty 7 and no product in stock
        Test case:
            1. Confirm the SO
            2. Cancel the line
        Expected result:
            1 Since no product in stock qty_backorder should be 7
            2 Line is cancelled, no more backorder => qty backorder should be 0
        """
        self.so1.action_confirm()
        self.so1.state = "sale"
        # Clear the context from _sale_order_create left over from creation
        self.so1.order_line[0].env.context = {}
        order_line = self.so1.order_line[0]
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(self.so1).values()
            self.assertEqual(values["lines"][0]["qty_backorder"], 7)
            with mock.patch("odoo.addons.queue_job.models.base.DelayableRecordset"):
                order_line.write(
                    {"product_qty_canceled": order_line.product_qty_remains_to_deliver}
                )
            values = mapper.map_record(self.so1).values()
            self.assertEqual(values["lines"][0]["qty_backorder"], 0)

    def test_bo_qty_changed(self):
        """Check sale order is sent when back order is modified.
        """
        # Make picking type with subcode so it is updated by delivery round
        pick_type = self.env["stock.picking.type"].search(
            [("name", "=", "Delivery Orders")], limit=1
        )
        pick_type.write({"subcode": "PICK"})
        stock_location = self.env.ref("stock.stock_location_stock")
        product = self.env["product.template"].create(
            {
                "name": "Unittest P1",
                "uom_id": self.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        sale_order = self.model.create(
            {
                "esb_ref": "ref_03",
                "partner_id": self.partner.id,
                "date_order": "2018-01-29",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": product.name,
                            "product_id": product.product_variant_ids.id,
                            "product_uom_qty": 7,
                        },
                    )
                ],
            }
        )
        assert sale_order.order_line[0].product_qty_unavailable == 7
        assert sale_order.order_line[0].current_product_qty_unavailable == 7
        sale_order.action_confirm()
        assert sale_order.order_line[0].product_qty_unavailable == 7
        assert sale_order.order_line[0].current_product_qty_unavailable == 7
        assert sale_order.picking_ids.picking_type_subcode == "PICK"
        # Changing the stock of the product should change the back order
        inventory = self.env["stock.inventory"].create(
            {"name": "Test", "location_id": stock_location.id, "filter": "partial"}
        )
        inventory.prepare_inventory()
        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": product.product_variant_id.id,
                "product_qty": 10,
                "location_id": stock_location.id,
            }
        )
        with mock.patch(
            "odoo.addons.queue_job.models." "base.DelayableRecordset"
        ) as export_record:
            inventory.action_done()
            self.assertEqual(export_record.call_count, 1)
        # Cache refreshing needed for the back order calculation to work ?
        product.refresh()
        assert sale_order.order_line[0].current_product_qty_unavailable == 0
