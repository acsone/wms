# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

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
    picking_id = fields.Many2one[Picking](readonly="True", ondelete="cascade")
    picking_is_completed = fields.Boolean(related="picking_id.is_completed")
    partner_id = fields.Many2one[Partner](
        related="picking_id.partner_id", readonly=True
    )
    origin = fields.Char(related="picking_id.origin", readonly=True)
    move_line_id = fields.Many2one[StockMoveLine](
        string="Operation",
        domain=[("state", "=", "assigned")],
        index=True,  # Necessary for performance reasons on pickings unreservation (and move lines deletion)
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
    remaining_qty = fields.Float(
        "Qty Remaining",
        compute="_compute_remaining_qty",
    )
    qty = fields.Float(
        "Qty Done",
        compute="_compute_qty",
        store=True,
        readonly=False,
    )
    is_qty_exceeded = fields.Boolean(compute="_compute_is_qty_exceeded")
    is_surplus_qty_confirmed = fields.Boolean("Confirm received more than expected")
    expiration_date = fields.Datetime(
        string="Expiration date",
    )
    lot_name = fields.Char(
        "Lot Name",
        compute="_compute_lot_name",
        store=True,
        readonly=False,
    )
    lot_id = fields.Many2one[StockLot](string="Lot")
    is_transfer = fields.Boolean(
        help="Technical field that is set when user is doing the transfer action"
        "in order to bypass some operations"
    )

    @api.depends("move_line_id", "qty", "remaining_qty")
    def _compute_is_qty_exceeded(self) -> None:
        for rec in self:
            rec.is_qty_exceeded = bool(
                float_compare(
                    rec.qty,
                    rec.remaining_qty,
                    precision_rounding=rec.move_line_id.product_uom_id.rounding,
                )
                > 0
                if rec.move_line_id
                else False
            )

    @api.depends("move_line_id", "expiration_date")
    def _compute_lot_name(self) -> None:
        for wiz in self:
            lot_name = wiz.lot_name
            if wiz.expiration_date:
                lot_name = (
                    self.env["stock.lot"]
                    .new({"product_id": wiz.product_id.id})
                    ._calc_name_for_food(
                        wiz.expiration_date, use_default=True, default=lot_name
                    )
                )
            wiz.lot_name = lot_name

    def _is_parent_child(self, parent, child) -> bool:
        if child and parent:
            return child.parent_path.startswith(parent.parent_path)
        return False

    @api.depends("move_line_id")
    def _compute_qty(self) -> None:
        for wizard in self:
            wizard.qty = 0

    @api.depends("move_line_id", "expiration_date")
    def _compute_location_dest_id(self) -> None:
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
    def _compute_location_op_dest_id(self) -> None:
        for rec in self:
            loc = rec.move_line_id.location_dest_id
            while loc and not loc.usage == "view":
                loc = loc.location_id
            rec.location_op_dest_id = loc.id

    @api.depends("move_line_id")
    def _compute_lot_required(self) -> None:
        for rec in self:
            rec.lot_required = rec.product_id.tracking != "none"

    @api.depends("move_id.quantity_done")
    def _compute_remaining_qty(self) -> None:
        for rec in self:
            rec.remaining_qty = rec.move_id.product_uom_qty - rec.move_id.quantity_done

    def _split_move_line(self) -> StockMove:
        move_line = self.move_line_id
        initial_reserved_uom_qty = move_line.reserved_uom_qty
        qty_done_in_uom = move_line.product_uom_id._compute_quantity(
            move_line.qty_done, move_line.product_id.uom_id
        )
        move_line.reserved_uom_qty = qty_done_in_uom
        move_line_new = self.move_line_id.copy(
            default={
                "qty_done": 0.0,
                "reserved_uom_qty": initial_reserved_uom_qty - qty_done_in_uom,
            }
        )
        return move_line_new

    def _prepare_move_line_values(self) -> dict:
        self.ensure_one()
        return {
            "picking_id": self.move_id.picking_id.id,
            "move_id": self.move_id.id,
            "location_id": self.move_line_id.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "product_id": self.move_line_id.product_id.id,
        }

    def _add_move_line(self) -> StockMoveLine:
        return self.env["stock.move.line"].create(self._prepare_move_line_values())

    def _is_quantity_zero(self) -> bool:
        precision = self.move_line_id.product_uom_id.rounding
        if precision:
            quantity_zero = bool(
                float_compare(self.qty, 0, precision_rounding=precision) <= 0
            )
        else:
            quantity_zero = self.qty <= 0
        return quantity_zero

    def _add(self) -> None:
        quantity_zero = self._is_quantity_zero()
        if quantity_zero and not self.is_transfer:
            raise UserError(_("Quantity must be greater than 0"))
        if quantity_zero and self.is_transfer:
            return
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
        if (
            self.location_dest_id != current_operation.location_dest_id
        ):  # Location changed
            if self.location_dest_id.scrap_location:
                # Do not allow this as it is linked through the product to a
                # move to a non scrap location that will be considered as
                # sucessful
                # This was allowed in the wizard to only be able to log a
                # ticket but we don't process any qty
                return
            if current_operation.qty_done:  # split the move
                current_operation = self._split_move_line()
            current_operation.location_dest_id = self.location_dest_id
        if self.lot_name:
            move_line = move.move_line_ids.filtered(
                lambda ml, wiz=self: ml.lot_name == wiz.lot_name
                and ml.location_dest_id == wiz.location_dest_id
            ).exists()
            if move_line:
                move_line.qty_done += self.qty
                move_line.location_dest_id = self.location_dest_id
            else:
                if not current_operation.lot_id and not current_operation.qty_done:
                    move_line = current_operation
                else:
                    move_line = self._add_move_line()
                # Setting just those fields is sufficient to allow
                # Odoo creating or using an existing lot at move validation
                move_line.update(
                    {
                        "lot_name": self.lot_name,
                        "qty_done": self.qty,
                        "expiration_date": self.expiration_date,
                        "location_dest_id": self.location_dest_id,
                    }
                )
        else:
            current_operation.qty_done += self.qty

    def button_nextop(self) -> None:
        self.button_nextlot()
        self.update(
            {
                "move_line_id": False,
                "location_dest_id": False,
                "is_transfer": False,
            }
        )

    def button_nextlot(self) -> None:
        self._add()
        self.update(
            {
                "qty": False,
                "lot_id": False,
                "expiration_date": False,
                "lot_name": False,
                "is_surplus_qty_confirmed": False,
                "is_transfer": False,
            }
        )

    def button_nextdestloc(self) -> None:
        self._add()
        self.update(
            {
                "qty": False,
                "location_dest_id": False,
                "is_surplus_qty_confirmed": False,
                "is_transfer": False,
            }
        )

    def button_transfer(self) -> bool or dict:
        """
        Just validate and return the action or if True,.

        return the picking form
        """
        self.is_transfer = True
        self.button_nextop()
        res = self.picking_id.button_validate()
        if isinstance(res, bool) and res:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "stock.action_picking_form"
            )
            action.update(
                {
                    "res_id": self.picking_id.id,
                    "context": False,
                }
            )
            return action
        return res
