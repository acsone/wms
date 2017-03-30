# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PrintingPrinter(models.Model):
    _inherit = 'printing.printer'

    code = fields.Char()
