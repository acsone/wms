# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import uuid

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
        return self.sync(transactions=self._process_csv_lines(csv_lines[1:]))

    def _process_csv_lines(self, csv_lines):
        lines = []
        for values in csv_lines:
            if len(values) < 2:
                raise ValueError("Missing column in product line.")
            sku = values[0]
            qty = values[1]
            product = self._get_product_by_sku(sku)
            if product:
                line_id = str(uuid.uuid4())
                line = {"product_id": product.id, "qty": int(qty), "uuid": line_id}
                lines.append(line)
        return lines

    def _get_product_by_sku(self, sku):
        domain = self.authenticated_partner._get_product_domain()
        domain.append(("default_code", "=", sku))
        return self.env["product.product"].search(domain, limit=1)
