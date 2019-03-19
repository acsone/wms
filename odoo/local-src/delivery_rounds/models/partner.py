# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    round_itinerary_ids = fields.One2many(
        'round.itinerary.position',
        'partner_id',
        'Delivery Itineraries',
        readonly=True,
    )
