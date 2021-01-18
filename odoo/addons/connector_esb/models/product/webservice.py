# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ProductStockWebserviceMessage(Component):

    _name = "esb.webservice.message.product.stock"
    _inherit = ["esb.webservice.message.base"]
    _apply_on = ["product.product"]
    _usage = "ws.message.product.stock"

    def get_message(self, product_skus):
        products = self.env["product.product"].search(
            [("default_code", "in", product_skus)]
        )
        data = []
        for product in products:
            values = {
                "sku": product.default_code,
                "stock": product.product_tmpl_id.immediately_usable_qty,
                "erpStockCode": product.state_id.esb_ref or "",
            }
            data.append(values)
        return self._produce_xml(data, list_item_el="stockItem")


class ProductStockCNKWebserviceMessage(Component):

    _name = "esb.webservice.message.product.stock.cnk"
    _inherit = ["esb.webservice.message.base"]
    _apply_on = ["product.product"]
    _usage = "ws.message.product.stock.cnk"

    def get_message(self, product_cnks=None):
        ProductProduct = self.env["product.product"]

        domain = ProductProduct.get_cnk_products_domain()

        if product_cnks:
            domain.append(("cnk_code", "in", product_cnks))
            product_recs = ProductProduct.search(domain, order="cnk_code")
        else:
            product_recs = ProductProduct.search(domain, order="cnk_code")

        stock_by_product = product_recs.read(
            ["cnk_code", "immediately_usable_qty", "default_code"]
        )

        result = []
        for line in stock_by_product:
            quantity = line["immediately_usable_qty"]
            quantity = quantity if quantity >= 0 else 0

            result.append(
                {
                    "cnk": line["cnk_code"],
                    "quantity": quantity,
                    "pid": line["default_code"],
                }
            )

        return result


class ProductStockSKUWebserviceMessage(Component):

    _name = "esb.webservice.message.product.stock.sku"
    _inherit = ["esb.webservice.message.base"]
    _apply_on = ["product.product"]
    _usage = "ws.message.product.stock.sku"

    def get_message(self, product_skus=None):
        ProductProduct = self.env["product.product"]

        domain = ProductProduct.get_sku_products_domain()

        if product_skus:
            domain.append(("default_code", "in", product_skus))
            product_recs = ProductProduct.search(domain, order="default_code")
        else:
            product_recs = ProductProduct.search(domain, order="default_code")

        stock_by_product = product_recs.read(["immediately_usable_qty", "default_code"])

        result = []
        for line in stock_by_product:
            quantity = line["immediately_usable_qty"]
            quantity = quantity if quantity >= 0 else 0

            result.append({"quantity": quantity, "sku": line["default_code"]})

        return result
