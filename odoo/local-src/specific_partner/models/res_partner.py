# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    alcyon_category_id = fields.Many2one(
        'partner.alcyon_category',
        string='Alcyon category',
    )
