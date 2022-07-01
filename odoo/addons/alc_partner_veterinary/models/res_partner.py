# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    vet_depot_number = fields.Char(string="Depot number")
    vet_subscription_number = fields.Char(string="Subscription number")

    veterinary_group_ids = fields.Many2many(
        "veterinary.group",
        "res_partner_veterinary_group_rel",
        "res_partner_id",
        "veterinary_group_id",
        string="Veterinary Group",
    )
