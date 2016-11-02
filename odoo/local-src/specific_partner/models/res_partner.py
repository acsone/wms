# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    alcyon_category_id = fields.Many2one(
        'partner.alcyon_category',
        string='Alcyon category',
    )

    depot_number = fields.Char(string='Depot number')

    depot_number_visible = fields.Boolean(
        compute='_compute_depot_number_visible'
    )

    legal_entity = fields.Char(string='Legal entity')

    @api.depends('alcyon_category_id')
    def _compute_depot_number_visible(self):
        veterinary = self.env.ref('scenario.partner_category_veterinary')
        for partner in self:
            partner.depot_number_visible = (
                partner.alcyon_category_id == veterinary
            )
