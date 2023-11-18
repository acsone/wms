# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import orders_router


class TestOrdersCase(FastAPITransactionCase):
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
        cls.default_fastapi_router = orders_router
        vals_partner = {"name": "P", "ref": "1214"}
        cls.partner = cls.env["res.partner"].create(vals_partner)
        vals_product = {"name": "Product", "default_code": "REF"}
        cls.product = cls.env["product.product"].create(vals_product)

        cls.so_model = cls.env["sale.order"]
        vals_sale_order = cls._get_vals_sale_order()
        cls.sale_order = cls.so_model.create(vals_sale_order)
        cls.sale_order.suite_name = "suite_name"
        cls.sale_order.sale_channel_id = cls.env.ref(
            "alc_sale_channel.sale_channel_phone"
        ).id
