# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import uuid

from odoo import _

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    @restapi.method(
        [(["/csv"], "POST")],
        input_param=restapi.MultipartFormData(
            {"file": restapi.BinaryData(mediatypes=["text/csv"])}
        ),
        output_param=restapi.CerberusValidator("_cart_schema"),
    )
    def csv(self, file, **params):
        reader = csv.reader(file, delimiter=";")
        return self._csv(list(reader), **params)

    def _cart_schema(self):
        schema = super(CartService, self)._cart_schema()
        schema["import_warning_msg"] = {
            "type": "string",
            "required": False,
            "nullable": False,
        }
        return schema

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        if sale.import_warning_msg:
            json["import_warning_msg"] = sale.import_warning_msg
        return json

    def _csv(self, csv_lines, **params):
        # the input is not a real CSV file; we have the first line for cart info
        # the rest of the lines should be sku/qty
        if not len(csv_lines) > 1:
            raise ValueError("Not enough lines.")  # ERROR
        info = {}
        if len(csv_lines[0]) < 4:
            raise ValueError("Missing columns in contact line.")
        info["suite_name"] = csv_lines[0][0] or False
        info["customer_ref"] = csv_lines[0][1] or False
        # "email": first_line[2]
        info["note"] = csv_lines[0][3] or False
        self.update(**info)
        not_found_skus, transactions = self._csv_lines_to_transactions(csv_lines[1:])
        if not_found_skus:
            msg = _(
                "The following sku are unknown: %s\nThe corresponding lines have been ignored by the import process."
            ) % ", ".join(not_found_skus)
            cart = self._find_open_cart(params.get("uuid", None))
            cart.import_warning_msg = msg
        return self.sync(transactions=transactions)

    def _csv_lines_to_transactions(self, csv_lines):
        """ Return a tuple (list of sku not found, list of transactions to apply)
        from the csv lnes
        """
        lines = []
        not_found_skus = []
        skus = []
        for values in csv_lines:
            if len(values) < 2:
                raise ValueError("Missing column in product line.")
            skus.append(values[0])

        product_by_sku = self._get_product_by_sku(skus=skus)
        for values in csv_lines:
            sku = values[0]
            qty = values[1]
            product = product_by_sku.get(sku)
            if product:
                line_id = str(uuid.uuid4())
                line = {"product_id": product.id, "qty": int(qty), "uuid": line_id}
                lines.append(line)
            else:
                not_found_skus.append(sku)
        return not_found_skus, lines

    def _get_product_by_sku(self, skus):
        domain = self.authenticated_partner._get_product_domain()
        domain.append(("default_code", "in", skus))
        return {p.default_code: p for p in self.env["product.product"].search(domain)}
