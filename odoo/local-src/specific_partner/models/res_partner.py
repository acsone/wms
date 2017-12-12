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

    vet_depot_number = fields.Char(string='Depot number')
    vet_subscription_number = fields.Char(string='Subscription number')

    is_veterinary = fields.Boolean(
        compute='_compute_is_veterinary'
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

    # temporary field to get the data and make it
    # possible to create contacts by hand in Odoo
    suite = fields.Char(
        "Suite Name",
        readonly=True,
    )

    @api.depends('alcyon_category_id')
    def _compute_is_veterinary(self):
        veterinary = self.env.ref(
            'specific_partner.partner_category_veterinary')
        for partner in self:
            partner.is_veterinary = (
                partner.alcyon_category_id == veterinary
            )
