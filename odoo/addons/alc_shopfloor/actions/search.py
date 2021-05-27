# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class SearchAction(Component):
    """Provide methods to search records from scanner

    The methods should be used in Service Components, so a search will always
    have the same result in all scenarios.
    """

    _inherit = "shopfloor.search.action"

    # TODO: these methods shall be probably replaced by scan anything handlers

    def location_from_scan(self, barcode):
        model = self.env["stock.location"]
        if not barcode:
            return model.browse()
        return model.search(
            ["|", ("barcode", "=", barcode), ("name", "=", barcode)], limit=1
        )

    def package_from_scan(self, barcode):
        model = self.env["stock.quant.package"]
        if not barcode:
            return model.browse()
        return model.search([("name", "=", barcode)], limit=1)

    def picking_from_scan(self, barcode):
        model = self.env["stock.picking"]
        if not barcode:
            return model.browse()
        return model.search([("name", "=", barcode)], limit=1)

    def product_from_scan(self, barcode):
        model = self.env["product.product"]
        if not barcode:
            return model.browse()
        product = model.search(
            ["|", ("barcode", "=", barcode), ("default_code", "=", barcode)], limit=1
        )
        if not product:
            packaging = self.env["product.packaging"].search(
                [("product_tmpl_id", "!=", False), ("barcode", "=", barcode)], limit=1
            )
            product = packaging.product_tmpl_id.product_variant_id
        return product

    def lot_from_scan(self, barcode, operations=None):
        model = self.env["stock.production.lot"]
        if not barcode:
            return model.browse()
        domain = [("name", "=", barcode)]
        if operations:
            lots_ids = operations.mapped("pack_lot_ids.lot_id") | operations.mapped(
                "lot_ids"
            )
            domain.append(("id", "in", lots_ids.ids))
        return model.search(domain, limit=1)

    def generic_packaging_from_scan(self, barcode):
        model = self.env["product.packaging"]
        if not barcode:
            return model.browse()
        return model.search(
            [("barcode", "=", barcode), ("product_tmpl_id", "=", False)], limit=1
        )
