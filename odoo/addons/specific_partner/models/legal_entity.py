# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class LegalEntity(models.Model):
    _name = 'legal.entity'

    name = fields.Char(required=True, translate=True)

    _sql_constraints = [
        ('unique_name', 'unique(name)', _('This legal entity already exists'))
    ]
