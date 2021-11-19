# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

import requests

from odoo.addons.connector_esb.tests import common


def post_ret_status(url, data, headers, auth):
    resp = requests.Response()
    resp.status_code = 200
    resp.json = lambda: {
        "erp_id": "42",
        "increment_id": "1000000348",
        "lines": [{"line_number": 10, "created_id": 106}],
    }
    return resp


class ExportB2cCommon(common.ESBTestCase):
    @classmethod
    def setUpClass(cls):
        super(ExportB2cCommon, cls).setUpClass()
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
                "name": "EXISTING PARTNER",
                "is_b2c_customer": True,
                "partner_type": "student_like",
                "ref": "REF",
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
                "partner_type": "veterinary",
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
        cls.order = cls.env["sale.order"].create(
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
                # "sale_channel": logiweb, chronovet, etc*
            }
        )
        # note we can't put a b2c sale_channel since we don't depend on the specific b2c modules
