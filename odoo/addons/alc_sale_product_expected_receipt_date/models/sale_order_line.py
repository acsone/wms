# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    next_expected_date_for_receipt = fields.Date(
        string="Next expected date for receipt",
        compute="_compute_next_expected_date_for_receipt",
    )

    @api.multi
    def _get_next_receipt_expected_date_dict(self):
        """Return a dictionary by line id of the next expected date for receipt
        """
        ret = {}.fromkeys(self.ids)
        # disable translation into the name_get called by read_group for
        # the product_id
        StockMove = self.env["stock.move"].with_context(lang="")
        expected_date_field = StockMove._fields["date_expected"]
        original_group_operator = expected_date_field.group_operator
        # group line by wh since the qty depends of the wh
        line_ids_by_wh = defaultdict(list)
        for record in self:
            line_ids_by_wh[record.order_id.warehouse_id].append(record.id)
        try:
            expected_date_field.group_operator = "min"
            # TODO usage="supplier" into the domain????? Otherwise customer
            #  returns will be taken into account
            for warehouse, line_ids in line_ids_by_wh.items():
                so_lines = self.browse(line_ids)
                product_ids = so_lines.mapped("product_id").ids
                domain = [
                    ("product_id", "in", product_ids),
                    ("state", "=", "assigned"),
                    ("picking_id.picking_type_id.code", "=", "incoming"),
                    (
                        "location_dest_id",
                        "child_of",
                        warehouse.view_location_id.id,
                    ),
                ]
                res = {
                    item["product_id"][0]: item["date_expected"]
                    for item in StockMove.read_group(
                        domain, ["product_id", "date_expected"], ["product_id"]
                    )
                }
                for line in so_lines:
                    ret[line.id] = res.get(line.product_id.id)
            return ret
        finally:
            expected_date_field.group_operator = original_group_operator

    @api.depends("product_id", "order_id.warehouse_id")
    def _compute_next_expected_date_for_receipt(self):
        expected_date_by_lines = self._get_next_receipt_expected_date_dict()
        for line in self:
            line.next_expected_date_for_receipt = expected_date_by_lines[
                line.id
            ]
