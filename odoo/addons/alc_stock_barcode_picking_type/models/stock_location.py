# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    barcode_picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Barcode Picking Type",
        help="Define the type of picking to create when this location (or any "
        "children) is scanned",
    )

    def get_barcode_picking_type_id(self):
        """
        Return the type of picking to create for the given location when
        scanned by the barcode app
        """
        self.ensure_one()
        if self.barcode_picking_type_id:
            return self.barcode_picking_type_id

        parent_location = self.search(
            [("id", "parent_of", self.id), ("barcode_picking_type_id", "!=", None)],
            order="parent_left DESC",
            limit=1,
        )

        return parent_location.barcode_picking_type_id
