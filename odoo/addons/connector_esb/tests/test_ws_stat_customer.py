# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields

from .common import ESBXMLTestCase


class WSStatCustomerTestCase(ESBXMLTestCase):
    def setUp(self):
        super(WSStatCustomerTestCase, self).setUp()
        self.setup_records()

    def deliver_saleorder(self, sale_order):
        """ Confirm and deliver all product from the sale order."""
        sale_order.action_confirm()
        picks = sale_order.picking_ids.filtered(lambda r: r.state != "done")
        picks.force_assign()
        for op in picks.pack_operation_product_ids:
            op.write({"qty_done": op.ordered_qty})
        for pick in picks:
            pick.with_context(test_mode=True).do_transfer()
        # Force this to be set because the delivery is not enough
        sale_order.write({"state": "done"})
        for sol in sale_order.order_line:
            sol.write({"qty_delivered": sol.product_uom_qty})

    def setup_records(self):
        self.customer = self.env["res.partner"].create(
            {
                "ref": "94738475673",
                "name": "Joe",
                "street": "Chemin des Pins, 23",
                "street2": "",
                "zip": "1010",
                "city": "Lausanne",
                "country_id": 44,
                "phone": "021123123",
                "fax": "021121212",
                "email": "joe@ch.ch",
            }
        )
        cat_medic = self.env.ref("specific_data.product_categ_medoc")
        cat_medic.esb_ref = "MED"
        cat_medic.is_business_unit = True
        cat_materiel = self.env.ref("specific_data.product_categ_materiel")
        cat_materiel.esb_ref = "MAT"
        cat_materiel.is_business_unit = True
        cat_ali = self.env.ref("specific_data.product_categ_ali")
        cat_ali.is_business_unit = True
        cat_ali.esb_ref = "ALI"
        # Test with a sub category of medic
        cat_microb = self.env.ref("specific_data.product_categ_antimicrobiens")
        self.supplier = self.env["res.partner"].create(
            {"name": "Guerra", "supplier": True, "ref": "987654321"}
        )
        # Set the products
        product_model = self.env["product.product"]
        self.p1 = product_model.create(
            {
                "name": "KETOFEN 5MG 10CP",
                "default_code": "1021906",
                "categ_id": cat_microb.id,
                "seller_ids": [
                    (0, 0, {"name": self.supplier.id, "product_code": "supplier001"})
                ],
            }
        )
        self.p2 = product_model.create(
            {
                "name": "EASYPILL CAT 30x10GR",
                "default_code": "2970820",
                "categ_id": cat_ali.id,
                "seller_ids": [
                    (0, 0, {"name": self.supplier.id, "product_code": "supplier001"})
                ],
            }
        )
        self.p3 = product_model.create(
            {
                "name": "CAGE PLIANTE DOG RESIDENCE 61x46x53cm",
                "default_code": "8332983",
                "categ_id": cat_materiel.id,
            }
        )
        # Creating sale order the stat takes only delivered quantity in account
        # One sale order for this year
        self.so1 = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "date_order": fields.Datetime.now(),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.p1.uom_id.id,
                            "product_uom_qty": 5,
                            "price_unit": 1799,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.p3.name,
                            "product_id": self.p3.id,
                            "product_uom": self.p3.uom_id.id,
                            "product_uom_qty": 5,
                            "price_unit": 141,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.p2.name,
                            "product_id": self.p2.id,
                            "product_uom": self.p2.uom_id.id,
                            "product_uom_qty": 7,
                            "price_unit": 10,
                        },
                    ),
                ],
            }
        )
        self.deliver_saleorder(self.so1)
        # One sale order for last year
        self.so2 = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "date_order": datetime.now() - timedelta(days=365),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.p1.uom_id.id,
                            "product_uom_qty": 5,
                            "price_unit": 1699,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.p3.name,
                            "product_id": self.p3.id,
                            "product_uom": self.p3.uom_id.id,
                            "product_uom_qty": 0,
                            "price_unit": 14,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.p2.name,
                            "product_id": self.p2.id,
                            "product_uom": self.p2.uom_id.id,
                            "product_uom_qty": 14,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )
        self.deliver_saleorder(self.so2)
        # An older sale order that should not be taken into account
        self.so3 = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "date_order": datetime.now() - timedelta(days=790),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.p1.uom_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.p3.name,
                            "product_id": self.p3.id,
                            "product_uom": self.p3.uom_id.id,
                            "product_uom_qty": 5,
                        },
                    ),
                ],
            }
        )
        self.deliver_saleorder(self.so3)

    def test_message(self):
        backend = self.env["esb.backend"].get_singleton()
        with backend.work_on("sale.order.line") as work:
            component = work.component("ws.message.customer.stat")
            message = component.get_message(self.customer.ref)
        self.assertXmlEquivalentData(
            message, self.read_test_file("customer_stat_ws_1.xml"), "productType"
        )
