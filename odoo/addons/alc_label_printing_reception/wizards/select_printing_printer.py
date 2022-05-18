# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class SelectPrintingPrinter(models.TransientModel):

    _name = "select.printing.printer"
    printer_id = fields.Many2one(comodel_name="printing.printer", string="Printer")

    def change_printer(self):
        for rec in self:
            if self.env.user.has_group(
                "alc_label_printing_reception.reception_change_printer"
            ):
                self.env.user.sudo().printing_product_label_printer_id = rec.printer_id
            else:
                raise UserError(
                    _("You don't have the permission to change the printer on users.")
                )
        return True
