# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base_report_to_printer.models.printing_printer import PrintingPrinter
from odoo.addons.base_report_to_printer.models.res_users import ResUsers as Users


class ResUsers(Users):

    printing_gls_printer_id = fields.Many2one[PrintingPrinter](string="Gls Printer")
