# -*- coding: utf-8 -*-
# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"
    _rec_name = "product_id"

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (
                    rec.id,
                    "%s (%d/%d)"
                    % (rec.product_id.display_name, rec.qty_done, rec.product_qty),
                )
            )
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Search a pack operation by name

        It is customized to find an operation by the display name of a product.
        The default name_search would search on the pack operation's name_get,
        which would be pretty inefficient due to the products' quantities in
        the name_get.

        This method also handles a fast path for when we are receiving products
        for a picking: in the reception wizard (stock.pack.operation.lot.add),
        the Many2one for stock.pack.operation filters on the picking_id. In
        that case, we limit the search on the products of the picking only.
        """
        args = args or []
        if name:
            # fast path for stock.pack.operation.lot.add, narrow the search
            # on the current picking
            picking_id = None
            product_args = []
            # default limit for search products a too large limit would be too
            # slow when the name match thousands of products
            product_limit = 100
            for (field, op, value) in args:
                if field == "picking_id" and op == "=":
                    picking_id = value
                    break
            if picking_id:
                picking = self.env["stock.picking"].browse(picking_id).exists()
                picking_products = picking.mapped("move_lines.product_id")
                product_args.append(("id", "in", picking_products.ids))
                # in this particular case we can disable the limit as we want
                # all the products of the picking, and we shouldn't have
                # thousands of them matching a term for a picking
                product_limit = None

            product_ids = [
                pid
                for pid, __ in self.env["product.product"].name_search(
                    name, operator=operator, args=product_args, limit=product_limit
                )
            ]
            args = [("product_id", "in", product_ids)] + args
        # Warning: as we limit on 100 products, if filter the pack operations
        # with 'args' and the name returns thousands of products (like 'a'),
        # then potentially we might have an empty list because the 'args'
        # domain would be applied on a list which does not include our product.
        # This is not a problem when using the fast path which should be the
        # common case.
        return self.search(args, limit=limit).name_get()


class StockPackOperationLotAdd(models.TransientModel):
    _name = "stock.pack.operation.lot.add"

    name = fields.Char(default="New")

    picking_id = fields.Many2one("stock.picking", readonly="True")
    partner_id = fields.Many2one(related="picking_id.partner_id", readonly=True)
    origin = fields.Char(related="picking_id.origin", readonly=True)

    operation_id = fields.Many2one(
        "stock.pack.operation", string="Operation", domain=[("state", "=", "assigned")]
    )

    def _is_parent_child(self, parent, child):
        if child.parent_left and child.parent_right:
            if parent.parent_left > child.parent_left:
                return False
            if parent.parent_right < child.parent_right:
                return False
            return True
        else:
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

    location_op_dest_id = fields.Many2one(
        "stock.location",
        "Operation Destination View Location",
        compute="_get_location_op_dest_id",
    )

    @api.one
    @api.depends("operation_id")
    def _get_location_op_dest_id(self):
        loc = self.operation_id.location_dest_id
        while loc and not loc.act_as_view:
            loc = loc.location_id
        self.location_op_dest_id = loc.id

    location_dest_id = fields.Many2one("stock.location", "Destination Location")

    lot_required = fields.Boolean("Lot Required", compute="_get_lot_required")

    @api.depends("operation_id")
    @api.one
    def _get_lot_required(self):
        self.lot_required = self.operation_id.product_id.tracking != "none"

    product_qty = fields.Float(related="operation_id.product_qty", readonly=True)
    product_uom_id = fields.Many2one(
        "product.uom", related="operation_id.product_uom_id", readonly=True
    )
    remaining_qty = fields.Float("Qty Remaining", compute="_get_remaining_qty")

    @api.depends("operation_id.qty_done")
    @api.one
    def _get_remaining_qty(self):
        self.remaining_qty = self.operation_id.product_qty - self.operation_id.qty_done

    qty = fields.Float("Qty Done")

    @api.onchange("qty")
    def _onchange_qty(self):
        if self.qty > self.remaining_qty:
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "You cannot receive more than the "
                        "expected remaining quantity"
                    ),
                }
            }

    life_date_char = fields.Char(string="Expiration date (input)")

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

    life_date = fields.Datetime(string="Expiration date")

    @api.onchange("life_date")
    def _onchange_life_date(self):
        oplot = self.env["stock.pack.operation.lot"]
        if self.life_date and self.operation_id:
            self.lot_name = oplot._calc_lotname_from_lifedate(
                self.operation_id, self.life_date
            )

    is_removal_date_expired = fields.Boolean(
        "Removal Date Expired", compute="_get_is_removal_date_expired"
    )

    @api.depends("life_date")
    def _get_is_removal_date_expired(self):
        oplot = self.env["stock.pack.operation.lot"]
        line = oplot.new(
            {"life_date": self.life_date, "operation_id": self.operation_id.id}
        )
        self.is_removal_date_expired = line.is_removal_date_expired

    lot_name = fields.Char("Lot Name")
    lot_id = fields.Many2one("stock.production.lot", "Lot")

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
            lot.onchange_life_date()
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
                rec.lot_id.onchange_life_date()
        return res

    def _add(self):
        if self.qty <= 0:
            raise UserError(_("Quantity must be greater than 0"))
        if self.qty > self.remaining_qty:
            raise UserError(
                _("You cannot receive more than the " "expected remaining quantity")
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
            # check Total
            if (
                sum(
                    [
                        max(lot.qty_todo, lot.qty)
                        for lot in self.operation_id.pack_lot_ids
                    ]
                )
                > self.operation_id.product_qty
            ):
                raise UserError(_("This lot is not in the list of expected lots"))
            pack.save()
        else:
            pack.write({"qty_done": self.qty})

    @api.multi
    def button_nextop(self):
        self.button_nextlot()
        self.operation_id = False

    @api.multi
    def button_nextlot(self):
        self._add()
        self.qty = False
        self.lot_id = False  # ensure we don't modify lot on next lines
        self.life_date = False
        self.life_date_char = False
        self.lot_name = False

    @api.multi
    def button_nextdestloc(self):
        self._add()
        self.qty = False
        self.location_dest_id = False

    def button_transfer(self):
        self.button_nextop()
        return self.picking_id.do_new_transfer()
