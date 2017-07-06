# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    pharmacist_id = fields.Many2one(
        comodel_name='res.partner',
        string='Associated pharmacist',
    )
    pharmacist_of_ids = fields.One2many(
        comodel_name='res.partner',
        inverse_name='pharmacist_id',
        string='Pharmacist associated to',
    )

    @api.depends('alcyon_category_id')
    def _compute_depot_number_visible(self):
        veterinary = self.env.ref(
            'specific_partner.partner_category_veterinary')
        for partner in self:
            partner.depot_number_visible = (
                partner.alcyon_category_id == veterinary
            )
