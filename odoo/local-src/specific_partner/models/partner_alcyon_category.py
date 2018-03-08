# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class PartnerAlcyonCategorie(models.Model):
    _name = 'partner.alcyon_category'

    name = fields.Char(
        string='Name',
        required=True
    )
    esb_ref = fields.Char(
        string='Reference for ESB',
        required=True,
    )
    _sql_constraints = [
        ('name_unique', 'unique(name)',
         _('This category name already exists')),
        ('esb_ref_unique', 'unique(esb_ref)',
         _('This reference esb already exists'))
    ]
