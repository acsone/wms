# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class AbcClassificationLevel(models.Model):

    _inherit = "abc.classification.level"
    _order = "percentage desc, id desc"

    name = fields.Selection(ABC_SELECTION, required=True)
