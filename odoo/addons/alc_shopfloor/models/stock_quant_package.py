# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models

from odoo.addons import decimal_precision as dp


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    shopfloor_weight = fields.Float(
        "Shopfloor weight (kg)",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_shopfloor_weight",
        help="Real pack weight or the estimated one.",
    )
    pack_operation_ids = fields.One2many(
        comodel_name="stock.pack.operation",
        inverse_name="package_id",
        readonly=True,
        help="Technical field. Pack operations moving this package.",
    )
    reserved_pack_operation_ids = fields.One2many(
        comodel_name="stock.pack.operation",
        compute="_compute_reserved_pack_operations",
    )

    def _get_reserved_pack_operations(self):
        return self.env["stock.pack.operation"].search(
            [("package_id", "=", self.id), ("state", "not in", ("done", "cancel"))]
        )

    @api.depends("pack_operation_ids.state")
    def _compute_reserved_pack_operations(self):
        for rec in self:
            rec.update(
                {"reserved_pack_operation_ids": rec._get_reserved_pack_operations()}
            )

    @api.depends("pack_weight", "estimated_pack_weight")
    def _compute_shopfloor_weight(self):
        for rec in self:
            rec.shopfloor_weight = rec.pack_weight or rec.estimated_pack_weight

    @api.constrains("name")
    def _constrain_name_unique(self):
        for rec in self:
            if self.search_count([("name", "=", rec.name), ("id", "!=", rec.id)]):
                raise exceptions.ValidationError(_("Package name must be unique!"))
