# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResLang(models.Model):
    _inherit = 'res.lang'

    esb_ref = fields.Char(string='Reference for ESB', copy=False)
