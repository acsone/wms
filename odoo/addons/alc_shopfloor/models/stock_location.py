# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.tools import float_compare


class StockLocation(models.Model):
    _inherit = "stock.location"

    shopfloor_picking_sequence = fields.Char(
        string="Shopfloor Picking Sequence",
        help="The picking done in Shopfloor scenarios will respect this order. "
        "The sequence is a char so it can be composed of fields such as "
        "'corridor-rack-side-level'. Pay attention to the padding "
        "('09' is before '19', '9' is not). It is recommended to use an"
        " Export then an Import to populate this field using a spreadsheet.",
    )
    reserved_pack_operation_ids = fields.One2many(
        comodel_name="stock.pack.operation",
        compute="_compute_reserved_pack_operation_ids",
    )

    def _get_reserved_pack_operation_ids(self):
        return self.env["stock.pack.operation"].search(
            [
                ("location_id", "child_of", self.id),
                ("product_qty", ">", 0),
                ("state", "not in", ("done", "cancel")),
            ]
        )

    def _compute_reserved_pack_operation_ids(self):
        for rec in self:
            rec.update(
                {"reserved_pack_operation_ids": rec._get_reserved_pack_operation_ids()}
            )

    def planned_qty_in_location_is_empty(self, pack_operation_ids=None):
        """Return if a location will be empty when pack operations will be confirmed

        Used for the "zero check". We need to know if a location is empty, but since
        we set the pack operations to "done" only at the end of the unload workflow, we
        have to look at the qty_done of the pack operations from this location.

        With `pack_operation_ids` we can force the use of the given pack operations for the check.
        This allows to know that the location will be empty if we process only
        these pack operations.
        """
        self.ensure_one()
        quants = self.env["stock.quant"].search(
            [("qty", ">", 0), ("location_id", "=", self.id)]
        )
        remaining = sum(quants.mapped("qty"))
        move_line_qty_field = "qty_done"
        if pack_operation_ids:
            pack_operation_ids = pack_operation_ids.filtered(
                lambda m: m.state not in ("cancel", "done")
            )
            move_line_qty_field = "product_qty"
        else:
            pack_operation_ids = self.env["stock.pack.operation"].search(
                [
                    ("state", "not in", ("cancel", "done")),
                    ("location_id", "=", self.id),
                    ("qty_done", ">", 0),
                ]
            )
        planned = remaining - sum(pack_operation_ids.mapped(move_line_qty_field))
        compare = float_compare(planned, 0, precision_rounding=0.01)
        return compare <= 0
