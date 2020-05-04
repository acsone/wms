# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class BankHoliday(models.Model):
    _name = "bank.holiday"

    name = fields.Char(required=True)
    date = fields.Date(required=True)
