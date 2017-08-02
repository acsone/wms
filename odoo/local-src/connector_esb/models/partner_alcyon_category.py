# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerAlcyonCategory(models.Model):
    _inherit = 'partner.alcyon_category'

    esb_ref = fields.Char(string='Reference for ESB')
