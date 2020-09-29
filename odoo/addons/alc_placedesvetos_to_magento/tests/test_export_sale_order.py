# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

import requests

import mock
from odoo.addons.connector_esb.tests import common


class TestExportSaleOrder(common.ESBTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestExportSaleOrder, cls).setUpClass()
        os.environ["ODOO_ESB_WS_USER"] = "ws_user"
        os.environ["ODOO_ESB_WS_BASE_URL"] = "https://test.com"
        os.environ["ODOO_ESB_WS_PWD"] = "pwd"
        # carrier
        cls.delivery = cls.env["delivery.carrier"].search(
            [("free_if_more_than", "=", False)], limit=1
        )
        cls.delivery.esb_ref = "03"
        # create a b2c_partner
        cls.b2c_partner = cls.env["res.partner"].create(
            {
                "name": "EXISTING placedesvetos PARTNER",
                "is_b2c_customer": True,
                "alcyon_category_id": cls.env.ref(
                    "specific_partner.partner_category_student"
                ).id,
                "ref": "PLACEDESVETOS_ABC",
                "email": "b2c@b2c.be",
            }
        )
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
        # create a vete
        cls.vt_partner = cls.env["res.partner"].create(
            {
                "name": "VT",
                "alcyon_category_id": cls.env.ref(
                    "specific_partner.partner_category_veterinary"
                ).id,
                "ref": "VTREF",
                "email": "vt@vt.be",
            }
        )

        # create a b2c sale_order
        cls.saleable_product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0001",
                "default_code": "12345",
            }
        )
        cls.placesdesvetos_order = cls.env["sale.order"].create(
            {
                "b2c_ref": "SO1",
                "partner_id": cls.b2c_partner.id,
                "partner_invoice_id": cls.vt_partner.id,
                "partner_shipping_id": cls.vt_partner.id,
                "carrier_id": cls.delivery.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "b2c_ref": "SOL1",
                            "product_id": cls.saleable_product.id,
                            "name": cls.saleable_product.name,
                            "product_uom": cls.saleable_product.uom_id.id,
                            "product_uom_qty": 10,
                        },
                    )
                ],
                "sale_channel": "placedesvetos",
            }
        )

    def post_ret_status(url, data, headers, auth):
        resp = requests.Response()
        resp.status_code = 200
        resp.json = lambda: {
            "erp_id": "42",
            "increment_id": "1000000348",
            "lines": [{"line_number": 10, "created_id": 106}],
        }
        return resp

    def test_00(self):
        """
        Data:
            A sale order with sale_channel set to PLACEDESVETOS
        Test case:
            Map SO info to ESB
        Expected result;
            The customer id into the exported data is the one from PLACEDESVETOS
            The sale_channel is 01 (phone)
        """
        with self.backend.work_on("sale.order") as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(self.placesdesvetos_order).values()
        self.assertEqual(
            values["customer_id"],
            self.env.ref("alc_placedesvetos.res_partner_placedesvetos").ref,
        )
        self.assertEqual(values["channel"], "01")

    @mock.patch("requests.post", side_effect=post_ret_status)
    def test_01(self, post):
        """
        Data:
            A sale order with sale_channel set to PLACEDESVETOS
        Test case:
            Export the SO to magento
        Expected result;
            The SO is exported
        """
        """Test export of a sale order catching the put request."""
        self.placesdesvetos_order.action_confirm()
        with self.backend.work_on("sale.order") as work:
            exporter = work.component(usage="record.exporter")
            exporter.run(self.placesdesvetos_order)
        post.assert_called_once()
        self.assertEqual(self.placesdesvetos_order.esb_ref, "1000000348")
