# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    printing_pharmacy_reception_printer_id = fields.Many2one(
        comodel_name="printing.printer", string="Pharmacy Reception Printer"
    )
