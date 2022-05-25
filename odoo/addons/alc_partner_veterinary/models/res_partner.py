# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    vet_depot_number = fields.Char(string="Depot number")
    vet_subscription_number = fields.Char(string="Subscription number")

    veterinary_group_id = fields.Many2one("veterinary.group", string="Veterinary Group")
