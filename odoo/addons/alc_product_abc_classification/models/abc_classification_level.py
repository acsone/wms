# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class AbcClassificationLevel(models.Model):

    _inherit = "abc.classification.level"
    _order = "percentage desc, id desc"

    name = fields.Selection(ABC_SELECTION, required=True)

    display_name = fields.Char(compute="_compute_display_name")

    @api.depends("name")
    def _compute_display_name(self):
        # required since name is a selection field... otherwise the display
        # name is the value not the label of the selection
        field_name = self._fields["name"]
        label_by_value = dict(field_name._description_selection(self.env))
        for rec in self:
            rec.display_name = label_by_value[rec.name]
