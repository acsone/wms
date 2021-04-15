# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


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
