# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RoundTemplate(models.Model):

    _inherit = "round.template"

    auto_close_picking_launched = fields.Boolean(
        string="Auto close picking launched", default=False
    )
    time_reopen_picking_launched = fields.Float(
        "Duration before departure to re open pickings", default=0.5
    )
