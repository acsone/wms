# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_printing_base.models.printing_printer import PrintingPrinter
from odoo.addons.base.models.res_users import Users


class ResUsers(Users):

    printing_pharmacy_reception_printer_id = fields.Many2one[PrintingPrinter](
        string="Pharmacy Reception Printer"
    )
