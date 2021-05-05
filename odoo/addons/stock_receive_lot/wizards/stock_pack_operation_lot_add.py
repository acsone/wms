# -*- coding: utf-8 -*-
# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPackOperationLotAdd(models.TransientModel):
    _name = "stock.pack.operation.lot.add"

    name = fields.Char(default="New")
    picking_id = fields.Many2one("stock.picking", readonly="True")
    partner_id = fields.Many2one(related="picking_id.partner_id", readonly=True)
    origin = fields.Char(related="picking_id.origin", readonly=True)
    operation_id = fields.Many2one(
        "stock.pack.operation", string="Operation", domain=[("state", "=", "assigned")]
    )
    location_op_dest_id = fields.Many2one(
        "stock.location",
        "Operation Destination View Location",
        compute="_compute_location_op_dest_id",
    )
    location_dest_id = fields.Many2one("stock.location", "Destination Location")

    lot_required = fields.Boolean("Lot Required", compute="_compute_lot_required")
    product_qty = fields.Float(related="operation_id.product_qty", readonly=True)
    product_id = fields.Many2one(
        "product.product", related="operation_id.product_id", readonly=True
    )
    product_uom_id = fields.Many2one(
        "product.uom", related="operation_id.product_uom_id", readonly=True
    )
    remaining_qty = fields.Float("Qty Remaining", compute="_compute_remaining_qty")
    qty = fields.Float("Qty Done")
    is_qty_exceeded = fields.Boolean(compute="_compute_is_qty_exceeded")
    is_surplus_qty_confirmed = fields.Boolean("Confirm received more than expected")
    life_date_char = fields.Char(string="Expiration date (input)")
    life_date = fields.Datetime(string="Expiration date")
    is_removal_date_expired = fields.Boolean(
        "Removal Date Expired", compute="_compute_is_removal_date_expired"
    )
    lot_name = fields.Char("Lot Name")
    lot_id = fields.Many2one("stock.production.lot", "Lot")

    @api.depends("qty", "remaining_qty")
    def _compute_is_qty_exceeded(self):
        for rec in self:
            rec.is_qty_exceeded = rec.qty > rec.remaining_qty

    def _is_parent_child(self, parent, child):
        if child.parent_left and child.parent_right:
            if parent.parent_left > child.parent_left:
                return False
            if parent.parent_right < child.parent_right:
                return False
            return True
        # parent_left/right could be deferred and it is disabled in init
        # mode during unittesting
        while child.location_id:
            if child.location_id == parent:
                return True
            child = child.location_id
        return False

    @api.onchange("operation_id")
    def _onchange_operation_id(self):
        op_dest_loc = self.operation_id.location_dest_id
        if op_dest_loc.usage == "internal" and not op_dest_loc.act_as_view:
            self.location_dest_id = op_dest_loc
        elif not (
            self.location_dest_id
            and self._is_parent_child(self.location_op_dest_id, self.location_dest_id)
        ):
            # If in the wizard, there is no location or if the current location
            # is not valid for selected operation then we need to update it
            self.location_dest_id = False
        self.life_date = False
        self.life_date_char = False
        self.lot_name = False
        self.qty = 0

    @api.depends("operation_id")
    def _compute_location_op_dest_id(self):
        for rec in self:
            loc = rec.operation_id.location_dest_id
            while loc and not loc.act_as_view:
                loc = loc.location_id
            rec.location_op_dest_id = loc.id

    @api.depends("operation_id")
    def _compute_lot_required(self):
        for rec in self:
            rec.lot_required = rec.product_id.tracking != "none"

    @api.depends("operation_id.qty_done")
    def _compute_remaining_qty(self):
        for rec in self:
            rec.remaining_qty = rec.operation_id.product_qty - rec.operation_id.qty_done

    @api.onchange("qty")
    def _onchange_qty(self):
        if self.is_qty_exceeded:
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "You received more than the expected remaining quantity. "
                        "Please confirm by ticking the 'Confirm received more "
                        "than expected' checkbox."
                    ),
                }
            }
        return None

    @api.onchange("life_date_char")
    def _onchange_life_date_char(self):
        if not self.life_date_char:
            self.life_date = False
        else:
            try:
                life_date = fields.Datetime.to_string(
                    datetime.strptime(self.life_date_char, "%d/%m/%Y")
                )
                self.life_date = life_date
            except Exception:
                self.life_date = False
        methods = self._onchange_methods.get("life_date", ())
        for method in methods:
            method(self)

    @api.onchange("life_date")
    def _onchange_life_date(self):
        oplot = self.env["stock.pack.operation.lot"]
        if self.life_date and self.operation_id:
            self.lot_name = oplot._calc_lotname_from_lifedate(
                self.operation_id, self.life_date
            )

    def _lot_onchange_life_date(self, lot):
        methods = lot._onchange_methods.get("life_date", ())
        for method in methods:
            method(lot)

    def _convert_lot_name2id(self, vals):
        if "operation_id" in vals:
            operation = self.env["stock.pack.operation"].browse(vals["operation_id"])
        else:
            operation = self.operation_id

        lot_obj = self.env["stock.production.lot"]
        lot = lot_obj.search(
            [
                ("name", "=", vals["lot_name"]),
                ("product_id", "=", operation.product_id.id),
            ]
        )
        if not lot:
            lot = lot_obj.create(
                {
                    "name": vals["lot_name"],
                    "life_date": vals.get("life_date", self.life_date),
                    "product_id": operation.product_id.id,
                }
            )
            self._lot_onchange_life_date(lot)
        vals["lot_id"] = lot.id

    @api.model
    def create(self, vals):
        if vals.get("lot_name"):
            self._convert_lot_name2id(vals)
        wiz = super(StockPackOperationLotAdd, self).create(vals)
        return wiz

    @api.multi
    def write(self, vals):
        if vals.get("lot_name"):
            for rec in self:
                rec._convert_lot_name2id(vals)
        res = super(StockPackOperationLotAdd, self).write(vals)
        for rec in self:
            if rec.lot_id and rec.life_date and rec.lot_id.life_date != rec.life_date:
                rec.lot_id.life_date = rec.life_date
                self._lot_onchange_life_date(rec.lot_id)
        return res

    def _add(self):
        if self.qty <= 0:
            raise UserError(_("Quantity must be greater than 0"))
        if self.is_qty_exceeded and not self.is_surplus_qty_confirmed:
            raise UserError(
                _(
                    "You receive more than the expected remaining quantity. "
                    "You must confirm that you received more than the expected qty"
                )
            )

        # A pack operation is for a destination and can have multiple lot lines
        # (pack_lot_ids) with the constraint that you cannot have 2 lot lines
        # with the same name (then we need to increase qty of existing line)
        # So while the destination stay the same, we can fill lines, otherwise
        # we need to split the pack operation and adjust the processed and
        # remaining quantities
        pack = self.operation_id
        if self.location_dest_id != pack.location_dest_id:  # Location changed
            if self.location_dest_id.scrap_location:
                # Do not allow this as it is linked through the product to a
                # move to a non scrap location that will be considered as
                # sucessful
                # This was allowed in the wizard to only be able to log a
                # ticket but we don't process any qty
                return
            if pack.qty_done:  # split pack
                pack2 = pack.copy(
                    default={
                        "qty_done": 0.0,
                        "product_qty": pack.product_qty - pack.qty_done,
                    }
                )
                pack.product_qty = pack.qty_done
                if self.operation_id.pack_lot_ids:
                    pack._copy_remaining_pack_lot_ids(pack2.id)
                pack = self.operation_id = pack2
            pack.location_dest_id = self.location_dest_id

        if self.lot_id:
            for lot in pack.pack_lot_ids:
                if lot.lot_id == self.lot_id:
                    lot.qty += self.qty
                    break
            else:
                pack.pack_lot_ids = [
                    (
                        0,
                        0,
                        {
                            "qty": self.qty,
                            "lot_name": self.lot_id.name,
                            "lot_id": self.lot_id.id,
                        },
                    )
                ]
            pack.save()
        else:
            pack.write({"qty_done": self.qty})

    @api.multi
    def button_nextop(self):
        self.button_nextlot()
        self.operation_id = False
        self.location_dest_id = False

    @api.multi
    def button_nextlot(self):
        self._add()
        self.qty = False
        self.lot_id = False  # ensure we don't modify lot on next lines
        self.life_date = False
        self.life_date_char = False
        self.lot_name = False
        self.is_surplus_qty_confirmed = False

    @api.multi
    def button_nextdestloc(self):
        self._add()
        self.qty = False
        self.location_dest_id = False
        self.is_surplus_qty_confirmed = False

    def button_transfer(self):
        self.button_nextop()
        return self.picking_id.do_new_transfer()
