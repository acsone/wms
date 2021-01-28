# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PickingZone(models.Model):

    _inherit = "picking.zone"

    abc_classification_profile_ids = fields.Many2many(
        comodel_name="abc.classification.profile",
        string="ABC Classification Profiles",
        relation="abc_classification_profile_picking_zone_rel",
        column1="picking_zone_id",
        column2="profile_id",
    )
