# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class RoundTag(models.Model):
    _name = 'round.tag'

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color Index')
