# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerAlcyonCategorie(models.Model):
    _name = 'partner.alcyon_category'

    name = fields.Char(required=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'This category name already exists')
    ]
