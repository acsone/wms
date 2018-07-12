# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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

    legal_entity_id = fields.Many2one(
        'legal.entity',
        string='Legal entity'
    )

    pharmacist_id = fields.Many2one(
        comodel_name='res.partner',
        string='Associated pharmacist',
    )
    pharmacist_of_ids = fields.One2many(
        comodel_name='res.partner',
        inverse_name='pharmacist_id',
        string='Pharmacist associated to',
    )

    master_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer master'
    )

    # temporary field to get the data and make it
    # possible to create contacts by hand in Odoo
    suite = fields.Char(
        "Suite Name",
    )
    call_name = fields.Char(
        string='Nickname'
    )

    @api.depends('alcyon_category_id')
    def _compute_is_veterinary(self):
        veterinary = self.env.ref(
            'specific_partner.partner_category_veterinary')
        for partner in self:
            partner.is_veterinary = (
                partner.alcyon_category_id == veterinary
            )

    @api.one
    @api.constrains('name', 'street', 'city', 'zip', 'country_id')
    def _is_valid_esb_address(self):
        """Check customer address validity.

        Invoicing and delivery address of customer are sent to the esb,
        and some fields are required for them to be valid.
        And check is made in the view as well.
        """
        if not self.parent_id or not self.customer:
            return
        if self.type not in ['invoice', 'delivery']:
            return
        if (self.name and self.street and self.city and
                self.zip and self.country_id.esb_ref):
            return
        raise ValidationError(_('For an invoicing or delivery address the '
                                'following fields (name, street, city, zip, '
                                'country) are required. And the country '
                                'must have a reference ESB.'))

    _sql_constraints = [
            ('ref_digit_only',
             "CHECK (ref SIMILAR TO '[[:digit:]]*')",
             _('The reference must be numeric or empty')
             )
    ]
