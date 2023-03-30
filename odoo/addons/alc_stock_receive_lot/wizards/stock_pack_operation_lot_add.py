# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock.models.stock_lot import StockLot
from odoo.addons.stock.models.stock_move import StockMove
from odoo.addons.stock.models.stock_move_line import StockMoveLine
from odoo.addons.stock.models.stock_picking import Picking
from odoo.addons.uom.models.uom_uom import UoM


class StockPackOperationLotAdd(models.TransientModel):
    _name = "stock.pack.operation.lot.add"
    _description = "Add a wizard that facilitates purchases reception."

    name = fields.Char(default="New")
    picking_id = fields.Many2one[Picking](readonly="True")
    partner_id = fields.Many2one[Partner](
        related="picking_id.partner_id", readonly=True
    )
    origin = fields.Char(related="picking_id.origin", readonly=True)
    move_line_id = fields.Many2one[StockMoveLine](
        string="Operation",
        domain=[("state", "=", "assigned")],
    )
    move_id = fields.Many2one[StockMove](related="move_line_id.move_id")
    location_op_dest_id = fields.Many2one[Location](
        string="Operation Destination View Location",
        compute="_compute_location_op_dest_id",
    )
    location_dest_id = fields.Many2one[Location](
        compute="_compute_location_dest_id",
        store=True,
        readonly=False,
        string="Destination Location",
    )

    lot_required = fields.Boolean(
        string="Lot Required", compute="_compute_lot_required"
    )
    product_qty = fields.Float(related="move_id.product_uom_qty", readonly=True)
    product_id = fields.Many2one[ProductProduct](
        related="move_line_id.product_id", readonly=True
    )
    product_uom_id = fields.Many2one[UoM](
        related="move_line_id.product_uom_id", readonly=True
    )
    remaining_qty = fields.Float("Qty Remaining", compute="_compute_remaining_qty")
    qty = fields.Float("Qty Done", compute="_compute_qty", store=True, readonly=False)
    is_qty_exceeded = fields.Boolean(compute="_compute_is_qty_exceeded")
    is_surplus_qty_confirmed = fields.Boolean("Confirm received more than expected")
    expiration_date_char = fields.Char(
        string="Expiration date (input)",
        compute="_compute_expiration_date_char",
        readonly=False,
        store=True,
    )
    expiration_date = fields.Datetime(
        string="Expiration date",
        compute="_compute_expiration_date",
        store=True,
    )
    lot_name = fields.Char(
        "Lot Name",
        compute="_compute_lot_name",
        store=True,
        readonly=False,
    )
    lot_id = fields.Many2one[StockLot](string="Lot")

    @api.depends("qty", "remaining_qty")
    def _compute_is_qty_exceeded(self):
        for rec in self:
            rec.is_qty_exceeded = rec.qty > rec.remaining_qty

    @api.depends("move_line_id", "expiration_date")
    def _compute_lot_name(self):
        for wiz in self:
            lot_name = wiz.lot_name
            if wiz.expiration_date:
                lot_name = (
                    self.env["stock.lot"]
                    .new({"product_id": wiz.product_id.id})
                    ._calc_name_for_food(wiz.expiration_date)
                )
            wiz.lot_name = lot_name

    @api.depends("move_line_id")
    def _compute_expiration_date_char(self):
        for wizard in self:
            wizard.update(
                {
                    "expiration_date": False,
                    "expiration_date_char": False,
                }
            )

    def _is_parent_child(self, parent, child):
        if child and parent:
            return child.parent_path.startswith(parent.parent_path)
        return False

    @api.depends("move_line_id")
    def _compute_qty(self):
        for wizard in self:
            wizard.qty = 0

    @api.depends("move_line_id", "expiration_date")
    def _compute_location_dest_id(self):
        for wiz in self:
            op_dest_loc = wiz.move_line_id.location_dest_id
            if op_dest_loc.usage == "internal":
                wiz.location_dest_id = op_dest_loc
            elif not (
                wiz.location_dest_id
                and wiz._is_parent_child(wiz.location_op_dest_id, wiz.location_dest_id)
            ):
                # If in the wizard, there is no location or if the current location
                # is not valid for selected operation then we need to update it
                wiz.location_dest_id = False

    @api.depends("move_line_id")
    def _compute_location_op_dest_id(self):
        for rec in self:
            loc = rec.move_line_id.location_dest_id
            while loc and not loc.usage == "view":
                loc = loc.location_id
            rec.location_op_dest_id = loc.id

    @api.depends("move_line_id")
    def _compute_lot_required(self):
        for rec in self:
            rec.lot_required = rec.product_id.tracking != "none"

    @api.depends("move_id.quantity_done")
    def _compute_remaining_qty(self):
        for rec in self:
            rec.remaining_qty = rec.move_id.product_uom_qty - rec.move_id.quantity_done

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

    @api.depends("expiration_date_char")
    def _compute_expiration_date(self):
        for wiz in self:
            try:
                expiration_date = fields.Datetime.to_string(
                    datetime.strptime(wiz.expiration_date_char, "%d/%m/%Y")
                )
                wiz.expiration_date = expiration_date
            except (TypeError, ValueError):
                wiz.expiration_date = False

    def _split_move(self):
        move = self.move_id
        move_line_new = move.copy(
            default={
                "quantity_done": 0.0,
                "product_qty": move.product_qty - move.quantity_done,
            }
        )
        self._level_move_line_quantities()
        self.move_line_id = move_line_new
        return move_line_new

    def _level_move_line_quantities(self):
        for move_line in self.move_id.move_line_ids:
            move_line.reserved_uom_qty = move_line.qty_done

    def _add_move_line(self):
        return self.env["stock.move.line"].create(
            {
                "move_id": self.move_id.id,
                "location_id": self.move_line_id.location_id.id,
                "location_dest_id": self.location_dest_id.id,
                "product_id": self.move_line_id.product_id.id,
            }
        )

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

        # A move is for a destination and can have multiple move lines. Each of these
        # lines can be linked to a single lot with the constraint that you cannot have
        # 2 lots with the same name (then we need to increase qty of existing line)
        # So while the destination stay the same, we can fill lines, otherwise
        # we need to split the move and adjust the processed and
        # remaining quantities
        move = self.move_id
        current_operation = self.move_line_id
        if self.location_dest_id != move.location_dest_id:  # Location changed
            if self.location_dest_id.scrap_location:
                # Do not allow this as it is linked through the product to a
                # move to a non scrap location that will be considered as
                # sucessful
                # This was allowed in the wizard to only be able to log a
                # ticket but we don't process any qty
                return
            if move.quantity_done:  # split the move
                move = self._split_move()
            move.location_dest_id = self.location_dest_id
        if self.lot_name:
            move_line = move.move_line_ids.filtered(
                lambda ml, wiz=self: ml.lot_name == wiz.lot_name
            ).exists()
            if move_line:
                move_line.qty_done += self.qty
            else:
                if not current_operation.lot_id and not current_operation.qty_done:
                    move_line = current_operation
                else:
                    move_line = self._add_move_line()
                move_line.lot_name = self.lot_name
                move_line.qty_done = self.qty
                move_line._create_and_assign_production_lot()
                if self.expiration_date and self.product_id.use_expiration_date:
                    move_line.lot_id.expiration_date = self.expiration_date

        else:
            current_operation.qty_done += self.qty

    def button_nextop(self):
        self.button_nextlot()
        self.move_line_id = False
        self.location_dest_id = False

    def button_nextlot(self):
        self._add()
        self.qty = False
        self.lot_id = False  # ensure we don't modify lot on next lines
        self.expiration_date = False
        self.expiration_date_char = False
        self.lot_name = False
        self.is_surplus_qty_confirmed = False

    def button_nextdestloc(self):
        self._add()
        self.qty = False
        self.location_dest_id = False
        self.is_surplus_qty_confirmed = False

    def button_transfer(self):
        self.button_nextop()
        return self.picking_id.button_validate()
