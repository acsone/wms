# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPackOperationSkipLot(models.TransientModel):

    _name = "stock.pack.operation.skip.lot"

    pack_operation_id = fields.Many2one(
        "stock.pack.operation",
        required=False,
        readonly=True,  # only into the UI since the record will be deleted by tthe doit
    )
    pack_lot_ids = fields.Many2many(
        "stock.pack.operation.lot", compute="_compute_pack_lot_ids"
    )
    skip_pack_lot_id = fields.Many2one(
        "stock.pack.operation.lot",
        string="Lot to skip",
        domain='[("id", "in", pack_lot_ids)]',
        required=False,  # only into the UI since the record will be deleted by tthe doit
    )

    @api.depends("pack_operation_id")
    def _compute_pack_lot_ids(self):
        for record in self:
            record.pack_lot_ids = self.pack_operation_id.pack_lot_ids.filtered(
                lambda pack_lot_id: pack_lot_id.qty < pack_lot_id.qty_todo
            )

    @api.multi
    def doit(self):
        for wizard in self:
            if not wizard.pack_operation_id or not wizard.skip_pack_lot_id:
                raise ValidationError(
                    _("Pack operation and the lot to skip are required informations")
                )
            wizard.pack_operation_id._skip_operation(wizard.skip_pack_lot_id)
        return {"type": "ir.actions.act_window_close"}
