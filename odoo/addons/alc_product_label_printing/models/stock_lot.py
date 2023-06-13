# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.alc_printing_base.utils import hw_print
from odoo.addons.stock.models.stock_lot import StockLot as Lot


class StockLot(Lot):
    def print_lot_label(self, quantity=1, printer_id=False):
        qty = quantity  # not affected by number_labels_to_print
        if qty:
            report = "alc_product_label_printing.report_lot_label"
            hw_print(self, report, qty=qty, printer_id=printer_id)
