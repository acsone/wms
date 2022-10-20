# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields

from odoo.addons.stock.models.stock_location import Location as LocationBase
from odoo.addons.stock.models.stock_picking import PickingType


class StockLocation(LocationBase, extends=True):  # type: ignore

    barcode_picking_type_id = fields.Many2one[PickingType](
        comodel_name="stock.picking.type",
        string="Barcode Picking Type",
        help="Define the type of picking to create when this location (or any "
        "children) is scanned",
    )

    def get_barcode_picking_type_id(self) -> PickingType:
        """
        Return the type of picking to create for the given location when.

        scanned by the barcode app
        """
        self.ensure_one()
        if self.barcode_picking_type_id:
            return self.barcode_picking_type_id
        parent_location = self.search(
            [("id", "parent_of", self.id), ("barcode_picking_type_id", "!=", None)],
            order="parent_path DESC",
            limit=1,
        )
        return parent_location.barcode_picking_type_id
