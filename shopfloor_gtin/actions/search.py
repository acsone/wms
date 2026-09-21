# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.osv.expression import OR

from odoo.addons.component.core import Component

from ..tools.barcodes_gtin import get_gtin_variants


class SearchAction(Component):
    _inherit = "shopfloor.search.action"

    def _extend_gtin_domain(self, barcode, domain):
        if gtin_variants := get_gtin_variants(barcode):
            domain = OR(
                [domain] + [[("barcode", "=", variant)] for variant in gtin_variants]
            )
        return domain

    def _find_product_domain(self, barcode):
        domain = super()._find_product_domain(barcode)
        domain = self._extend_gtin_domain(barcode, domain)
        return domain

    def _find_packaging_domain(self, barcode):
        domain = super()._find_packaging_domain(barcode)
        domain = self._extend_gtin_domain(barcode, domain)
        return domain
