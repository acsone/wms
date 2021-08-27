# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AnimalSpecies(models.Model):

    _name = "animal.species"

    name = fields.Char(translate=True)
