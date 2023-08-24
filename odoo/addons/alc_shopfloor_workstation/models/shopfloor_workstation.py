# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base_report_to_printer.models.printing_printer import PrintingPrinter
from odoo.addons.shopfloor_workstation.models.shopfloor_workstation import (
    ShopfloorWorkstation as ShopfloorWorkstationBase,
)


class ShopfloorWorkstation(ShopfloorWorkstationBase):

    printing_product_label_printer_id = fields.Many2one[PrintingPrinter](
        string="Product Label Printer"
    )
    printing_package_label_printer_id = fields.Many2one[PrintingPrinter](
        string="Package Label Printer"
    )

    def set_as_default_on_user(self, user):
        res = super().set_as_default_on_user(user)
        if self.printing_product_label_printer_id:
            user.printing_product_label_printer_id = (
                self.printing_product_label_printer_id
            )
        if self.printing_package_label_printer_id:
            user.default_label_printer_id = self.printing_package_label_printer_id
        return res
