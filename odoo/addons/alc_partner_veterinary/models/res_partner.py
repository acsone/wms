# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_partner_type.models import res_partner


class ResPartner(res_partner.ResPartner):

    vet_depot_number = fields.Char(string="Depot number")
    vet_subscription_number = fields.Char(string="Subscription number")
