# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.alc_printing_base.utils import hw_print
from odoo.addons.product.models.product_product import ProductProduct as Product


class ProductProduct(Product):
    def print_product_label(self, quantity=1, printer_id=False):
        self.ensure_one()
        qty = quantity
        if qty:
            hw_print(
                self,
                "alc_product_label_printing.report_lot_nolot_label",
                qty=qty,
                printer_id=printer_id,
            )
