# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VeterinaryGroup(models.TransientModel):

    _name = "veterinary.group.user.wizard"
    _description = "Wizard to add Partners to Veterinary Groups."

    veterinary_group_id = fields.Many2one("veterinary.group", string="Veterinary Group")
    partner_ids = fields.Many2many("res.partner", string="Partners")

    def execute(self):
        for wizard in self:
            vals = {"veterinary_group_id": wizard.veterinary_group_id.id}
            wizard.partner_ids.write(vals)
        return True
