# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from .common import TestFacadeMixin


class TestPSaleOrder(TransactionCase, TestFacadeMixin):
    @classmethod
    def _get_vals_sale_line(cls, product):
        return {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": 1,
            "product_uom": product.uom_id.id,
            "price_unit": 10,
        }

    @classmethod
    def _get_vals_sale_order(cls, partner=None, products=None):
        products = products or cls.product
        return {
            "partner_id": (partner or cls.partner).id,
            "order_line": [(0, 0, cls._get_vals_sale_line(p)) for p in products],
        }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._init_data()
        vals_partner = {"name": "P", "ref": "1214"}
        cls.partner.write(vals_partner)
        vals_product = {"name": "Product", "default_code": "REF"}
        cls.product = cls.env["product.product"].create(vals_product)
        cls.so_model = cls.env["sale.order"]
        vals_sale_order = cls._get_vals_sale_order()
        cls.sale_order = cls.so_model.create(vals_sale_order)
        cls.sale_order.suite_name = "suite_name"
        cls.sale_order.sale_channel_id = cls.env.ref(
            "alc_sale_channel.sale_channel_phone"
        ).id

    def test_sale_order(self):
        sales_order_facade = self._get_service_facade("sales_order")
        result, _error, _location = sales_order_facade(since="1900-01-01")
        expeced_result = f"""<?xml version="1.0" encoding="UTF-8" ?>
            <data>
                <order>
                    <web_id>{self.sale_order.id}</web_id>
                    <erp_name>{self.sale_order.name}</erp_name>
                    <suite_name>suite_name</suite_name>
                    <date>{self.sale_order.date_order_short}</date>
                    <client_order_ref></client_order_ref>
                    <lines>
                        <line>
                            <line_id>{self.sale_order.order_line.id}</line_id>
                            <qty_ordered>1.0</qty_ordered>
                            <qty_delivered>0.0</qty_delivered>
                            <qty_canceled>0.0</qty_canceled>
                            <sku>REF</sku>
                        </line>
                    </lines>
                </order>
            </data>"""
        self.assertXmlEqual(expeced_result, result)
