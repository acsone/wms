# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import random

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .. import constants


class StockPicking(models.Model):
    _inherit = "stock.picking"

    checksum = fields.Char("Checksum", copy=False)
    zetes_state = fields.Selection(
        [
            (constants.AS_DEFAULT, "Default"),
            (constants.AS_START, "Start"),
            (constants.AS_ACTIVE, "Active"),
            (constants.AS_STAGING, "Staging"),
            (constants.AS_DONE, "Done"),
            ("passport", "Passport"),
            (constants.AS_CANCELED, "Canceled"),
            (constants.AS_FINISHED, "Finished"),
        ],
        string="Zetes state",
        default=constants.AS_DEFAULT,
        copy=False,
        required=True,
        track_visibility="onchange",
    )
    zetes_state_lastchange = fields.Datetime("Last Zetes state change")
    is_zetes_error = fields.Boolean("Zetes error", copy=False)
    nbr_actions = fields.Integer(
        "Nbr of actions", compute="_compute_nbr_actions", readonly=True
    )
    is_passport_required = fields.Boolean("Passport required", default=False)
    zetes_logger_ids = fields.One2many(
        comodel_name="zetes.logger", inverse_name="picking_id", string="Zetes logger"
    )
    zetes_logger_count = fields.Integer(
        compute="_compute_zetes_logger_count", string="# of Zetes logs"
    )
    zetes_logger_requires_check = fields.Boolean(
        compute="_compute_zetes_logger_requires_check", store=True
    )

    @api.depends("zetes_logger_ids", "zetes_logger_ids.to_check")
    def _compute_zetes_logger_requires_check(self):
        for record in self:
            record.zetes_logger_requires_check = any(
                record.zetes_logger_ids.mapped("to_check")
            )

    def _compute_zetes_logger_count(self):
        zetes_logger_groups = self.env["zetes.logger"].read_group(
            domain=[("picking_id", "in", self.ids)],
            fields=["picking_id"],
            groupby=["picking_id"],
        )
        for group in zetes_logger_groups:
            picking = self.browse(group["picking_id"][0])
            picking.zetes_logger_count = group["picking_id_count"]

    @api.model
    def create(self, vals):
        record = super(StockPicking, self).create(vals)
        if "zetes_state" in vals:
            record.zetes_state_change()
        return record

    @api.multi
    def write(self, vals):
        result = super(StockPicking, self).write(vals)
        if "zetes_state" in vals:
            self.zetes_state_change()
        return result

    def zetes_state_change(self):
        self.zetes_state_lastchange = fields.Datetime.now()

    @api.model
    def default_get(self, fields_list):
        # Prevent any default value to be set for zetes technical data.
        # If you search in the view, then searched value is given as default
        # value in the context. Without doing this, the backorder (created by
        # copy) will get the value no matter of copy=False
        res = super(StockPicking, self).default_get(fields_list)
        if "zetes_state" in res:
            res["zetes_state"] = constants.AS_DEFAULT
        if "checksum" in res:
            del res["checksum"]
        if "is_zetes_error" in res:
            del res["is_zetes_error"]
        return res

    def _prepare_assign_operator_values(self):
        values = super(StockPicking, self)._prepare_assign_operator_values()
        zetes_operator_uid = self.env.context.get("zetes_operator_uid")
        if zetes_operator_uid:
            values["operator_id"] = zetes_operator_uid
        return values

    @api.multi
    def assign_picking_checksum(self):
        active_picking_query = """
        SELECT checksum
        FROM stock_picking
        WHERE checksum IS NOT NULL
        AND state IN ('assigned', 'partially_available')
        """
        self.env.cr.execute(active_picking_query)
        active_picking_checksum = {row[0] for row in self.env.cr.fetchall()}
        picking_checksums = {format(i, "0%d" % 2) for i in range(1, 100)}

        checksum_available = picking_checksums - active_picking_checksum
        if not checksum_available:
            raise Warning("There is no picking checksum available")

        for picking in self:
            if picking.checksum:
                continue

            checksum = random.choice(list(checksum_available))
            checksum_available.remove(checksum)
            picking.checksum = checksum

    @api.multi
    def interrupt_picking(self):
        wo_checksum = self.filtered(lambda p: not p.checksum)
        if wo_checksum:
            wo_checksum.assign_picking_checksum()
        self.write({"operator_id": None})

    @api.multi
    def validate_picking(self):
        for picking in self.filtered(lambda p: not p.zetes_logger_requires_check):
            # The method "do_new_transfer" is the method called when
            # an user click on "Validate" on a picking.
            result = picking.do_new_transfer()

            # TO BE REMOVED ... this code is already implemented into
            # stock_picking_backorder

            # In Odoo this button will open a wizard in following case:
            # 1. A wizard if no quantity has been defined on lines
            #   (this wizard will set the quantity on each lines)
            # 2. A wizard if we need to create a back order
            if isinstance(result, dict) and result:
                model = result.get("res_model")
                wizard = self.env[model].browse(int(result.get("res_id")))

                # Fortunately these wizards have the same
                # method "process" to execute the wizard
                wizard.process()

    @api.multi
    def _compute_nbr_actions(self):
        for picking in self:
            lines = picking.pack_operation_ids
            lines = lines.filtered(
                lambda line: int(line.qty_done) != int(line.product_qty)
                and line.zetes_state
                in [constants.OP_DEFAULT, constants.OP_SKIPPED, constants.OP_CANCELED]
            )
            split_lines = lines.split_pack_op_lines()
            picking.nbr_actions = len(split_lines)

    def _lock_rows(self):
        """Lock the database rows of the pickings to prevent concurrent access
        in case two consecutive requests are sent for the same pickings.

        The lock is released when the transaction is committed or rolled back.
        """
        if self:
            self.env.cr.execute(
                "SELECT id FROM stock_picking WHERE id in %s FOR UPDATE",
                (tuple(self.ids),),
            )


class PackOperationReserveRel(models.Model):
    _name = "pack.operation.reserve.rel"

    pack_operation_id = fields.Many2one(
        "stock.pack.operation", string="Pack operation", required=True
    )
    reserve_location_id = fields.Many2one(
        "stock.location", string="Reserve", required=True
    )
    lot_id = fields.Many2one("stock.production.lot", string="Lot")


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    zetes_state = fields.Selection(
        [
            (constants.OP_DEFAULT, "Default"),
            (constants.OP_PICKED, "Picked"),
            (constants.OP_SHORTPICKED, "Shortpicked"),
            (constants.OP_SKIPPED, "Skipped"),
            (constants.OP_CUT, "Cut"),
            (constants.OP_CANCELED, "Canceled / Full"),
            (constants.OP_MISSING, "Missing"),
        ],
        string="Zetes state",
        default=constants.OP_DEFAULT,
        required=True,
    )

    @api.multi
    def split_pack_op(self, new_qty, location_dest_id, lot_id=None):
        """
        Split the current pack operation in two pack operation.
        One with the previous destination and a new one with the new
        destination (location_dest_id) and the a specific quantity (new_qty).

        1. Check the quantity (the new quantity cannot be greater than
        the available quantity)
        2. Create the new pack operation
        3. (Optional) Reduce the quantity on the pack operation lot
        4. Reduce the quantity on the pack operation
        :param new_qty:
        :param location_dest_id:
        :param lot_id:
        :return:
        """
        self.ensure_one()

        # Step 1
        quantity_available = self.product_qty - self.qty_done
        if new_qty > quantity_available:
            raise UserError(
                _(
                    "You cannot split this pack operation because "
                    "the new quantity (%s) is geater than "
                    "the available quantity (%s)"
                )
                % (new_qty, quantity_available)
            )

        # Step 2
        new_pack = self.copy(
            {
                "qty_done": 0.0,
                "product_qty": new_qty,
                "location_dest_id": location_dest_id,
            }
        )

        # Step 3
        if lot_id:
            if not self.pack_lot_ids:
                raise UserError(_("No pack operation found"))
            pack_lot = self.pack_lot_ids.filtered(lambda line: line.lot_id.id == lot_id)
            if not pack_lot:
                raise UserError(_("No pack operation found with ID %s" % lot_id))

            lot_quantity_available = pack_lot.qty_todo - pack_lot.qty
            if new_qty > lot_quantity_available:
                raise UserError(
                    _(
                        "You cannot split this pack operation lot because "
                        "the new quantity (%s) is greater than "
                        "the available quantity (%s)"
                    )
                    % (new_qty, lot_quantity_available)
                )

            pack_lot.copy({"operation_id": new_pack.id, "qty_todo": new_qty, "qty": 0})

            pack_lot.write({"qty_todo": pack_lot.qty_todo - new_qty})

        # Step 4
        self.write({"product_qty": self.product_qty - new_qty})

        return new_pack

    @api.multi
    def add_qty(self, qty, lot_id=None):
        """
        Add a qty on the pack operation
        :param qty: int - the qty to add
        :param lot_id: int - the ID of the lot
        :return:
        """
        self.ensure_one()

        if not qty:
            return

        self.qty_done += qty

        if not lot_id:
            return

        # When we have the lot, we will check if there no existing
        # quantity for this lot.
        pack_lot = self.pack_lot_ids.filtered(lambda line: line.lot_id.id == lot_id)

        # If there no existing line (quantity) for this lot
        # we will create a new line
        if not len(pack_lot):
            self.pack_lot_ids.create(
                {"operation_id": self.id, "qty": qty, "lot_id": lot_id}
            )
        # Otherwise we set the quantity for this lot
        # We don't need to add the new quantity to the lot
        # because Zetes send one request by lot
        else:
            pack_lot.qty += qty

    @api.multi
    def put_in_reserve(self, reserve_id):
        """
        Put the remaining quantity in the reserve
        1. Split the pack operation to create the operation to the reserve
        2. Reduce the quantity to do to the quantity done
        3. (Optional) Reduce the quantity to do on the pack log to
        the quantity done and remove empty pack operation lot
        :param reserve_id:
        :return:
        """
        # If no quantity has been taken, we simply change the destination
        # of the current pack operation and set the quantity on the pack
        # operation and pack operation lots
        if not self.qty_done:
            self.write({"qty_done": self.product_qty, "location_dest_id": reserve_id})

            for pack_lot in self.pack_lot_ids:
                pack_lot.write({"qty": pack_lot.qty_todo})
            return

        quantity_remaining = self.product_qty - self.qty_done

        # Step 1
        new_pack = self.copy(
            {
                "qty_done": quantity_remaining,
                "product_qty": quantity_remaining,
                "location_dest_id": reserve_id,
            }
        )

        # Step 2
        self.write({"product_qty": self.qty_done})

        # Step 3
        pack_lot_to_unlink = self.env["stock.pack.operation.lot"]
        pack_lot_obj = self.env["stock.pack.operation.lot"]
        for pack_lot in self.pack_lot_ids:
            if pack_lot.qty_todo == pack_lot.qty:
                continue
            qty = pack_lot.qty
            qty_todo = pack_lot.qty_todo

            qty_remaining = qty_todo - qty
            pack_lot_obj.create(
                {
                    "operation_id": new_pack.id,
                    "qty": qty_remaining,
                    "qty_todo": qty_remaining,
                    "lot_id": pack_lot.lot_id.id,
                }
            )

            if not pack_lot.qty:
                pack_lot_to_unlink |= pack_lot
            else:
                pack_lot.write({"qty_todo": pack_lot.qty})

        pack_lot_to_unlink.unlink()

    @api.multi
    def split_pack_op_lines(self):
        result = []

        for line in self:
            if not line.pack_lot_ids:
                result.append((line, None))
                continue

            pack_op_lots = line.pack_lot_ids.sorted(
                lambda lot_line: lot_line.lot_id.removal_date
            )
            for pack_op_lot in pack_op_lots:
                if pack_op_lot.qty < pack_op_lot.qty_todo:
                    result.append((line, pack_op_lot))

        return result


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_portable_printer = fields.Boolean("Portable printer", default=False)
