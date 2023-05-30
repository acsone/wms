# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.alc_printing_base.models.printing_printer import PrintingPrinter


class SelectPharmacyPrintingPrinter(models.TransientModel):

    _name = "select.pharmacy.printing.printer"
    _description = "Pharmacy printing printer selection wizard"

    printer_id = fields.Many2one[PrintingPrinter](string="Printer")

    def doit(self):
        for rec in self:
            self.env.user.sudo().printing_pharmacy_reception_printer_id = rec.printer_id
        return True
