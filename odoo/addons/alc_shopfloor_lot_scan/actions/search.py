# Copyright 2023 ACSONE SA/NV (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import re

from odoo.addons.shopfloor.actions.search import SearchAction as SearchActionBase

LOT_BARCODE = re.compile(r"#(?P<product_default_code>\w+)#(?P<lot_name>\w+)#?")


class SearchAction(SearchActionBase):
    def lot_from_scan(self, barcode, products=None, limit=1):
        m = LOT_BARCODE.match(barcode)
        if m and len(m.groups()) == 2:
            barcode = m.group("lot_name")
            product_codes = m.group("product_default_code")
            products = self.env["product.product"].search(
                [("default_code", "=", product_codes)]
            )
        return super().lot_from_scan(barcode, products=products, limit=limit)
