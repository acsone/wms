import logging

import odoo
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError

from .. import constants

_logger = logging.getLogger(__name__)


class ManageUOP(models.TransientModel):
    _name = "manage.uop"

    user_id = fields.Many2one("res.users", string="User")
    uop = fields.Integer("UOP")
    picking_id = fields.Many2one("stock.picking", string="UOP")
    picking_name = fields.Char(
        "Picking name", related="picking_id.display_name", readonly=True
    )
    picking_uop = fields.Integer("Picking UOP", related="picking_id.id", readonly=True)
    picking_zone_id = fields.Many2one(
        "picking.zone",
        string="Picking Zone",
        related="picking_id.picking_type_id.picking_zone_id",
        readonly=True,
    )
    picking_zone_code = fields.Char(
        string="Picking Zone Code", related="picking_zone_id.code", readonly=True
    )
    picking_checksum = fields.Char(
        "Picking checksum", related="picking_id.checksum", readonly=True
    )
    line_ids = fields.One2many("manage.uop.line", "wizard_id", string="Lines")
    picking_line_ids = fields.One2many(
        "view.picking.line", "wizard_id", string="Picking Lines", readonly=True
    )
    is_change_lots = fields.Boolean("Change lots")
    printer_num = fields.Integer(string="Printer", default=1, required=True)
    nbr_package = fields.Integer("Nbr package", default=1, required=True)
    state = fields.Selection(
        [
            ("start_menu", "Start Menu"),
            ("search_picking", "Search Picking"),
            ("main_menu", "Main Menu"),
            ("view_picking", "View Picking"),
            ("validate_picking", "Validate Picking"),
        ],
        default="start_menu",
    )

    def search_picking(self):
        self.ensure_one()

        if self.uop:
            pickings = self.env["stock.picking"].search(
                [
                    ("id", "=", self.uop),
                    ("state", "in", ("partially_available", "assigned")),
                    ("picking_type_subcode", "=", "PICK"),
                ]
            )
            if not pickings:
                raise UserError(_("UOP not found or this UOP is not open"))
        elif self.user_id:
            pickings = self.env["stock.picking"].search(
                [
                    ("operator_id", "=", self.user_id.id),
                    ("state", "in", ("partially_available", "assigned")),
                    ("picking_type_subcode", "=", "PICK"),
                ]
            )
        else:
            raise UserError(_("Please insert the UOP or the user"))

        if not pickings:
            raise UserError(_("You do not have an UOP"))

        if len(pickings) == 1:
            self.picking_id = pickings.id
            self.state = "main_menu"
        else:
            self.state = "search_picking"

        return self.reload_page()

    def go_to_main_menu(self):
        self.state = "main_menu"

        if not self.picking_id:
            raise UserError(_("Please select an UOP"))

        return self.reload_page()

    def to_to_validate_picking(self):
        self.state = "validate_picking"

        self.line_ids.unlink()

        line_to_update = self.picking_id.pack_operation_ids.filtered(
            lambda line: line.zetes_state == constants.OP_MISSING and line.pack_lot_ids
        )

        self.is_change_lots = len(line_to_update)
        for pack_op in line_to_update:
            line_done = pack_op.pack_lot_ids.filtered(lambda pack_lot: pack_lot.qty)

            self.line_ids.create(
                {
                    "wizard_id": self.id,
                    "pack_op_id": pack_op.id,
                    "lot_id": len(line_done) == 1 and line_done.lot_id.id or None,
                    "qty": pack_op.product_qty,
                }
            )

        return self.reload_page()

    def view_picking(self):
        self.state = "view_picking"

        self.picking_line_ids.unlink()
        for pack_op in self.picking_id.pack_operation_ids:
            if pack_op.pack_lot_ids:
                for pack_lot in pack_op.pack_lot_ids:
                    self.picking_line_ids.create(
                        {
                            "wizard_id": self.id,
                            "pack_op_id": pack_op.id,
                            "lot_id": pack_lot.lot_id.id,
                            "qty_done": pack_lot.qty,
                            "qty_todo": pack_lot.qty_todo,
                        }
                    )
            else:
                self.picking_line_ids.create(
                    {
                        "wizard_id": self.id,
                        "pack_op_id": pack_op.id,
                        "qty_done": pack_op.qty_done,
                        "qty_todo": pack_op.product_qty,
                    }
                )

        return self.reload_page()

    def validate(self):
        self.ensure_one()

        for line in self.line_ids:
            if not line.lot_id:
                raise UserError(_("Please set a lot"))

            if line.qty > line.pack_op_id.product_qty:
                raise UserError(
                    _("You cannot pick more than %s unit of the product %s")
                    % (
                        line.pack_op_id.product_qty,
                        line.pack_op_id.product_id.display_name,
                    )
                )

            line.pack_op_id.qty_done = 0
            line.pack_op_id.pack_lot_ids.unlink()
            line.pack_op_id.add_qty(line.qty, lot_id=line.lot_id.id)

        if not self.printer_num:
            raise UserError(_("Please select the printer"))

        printer_toshiba = self.env["printing.printer"].search(
            [("code", "=", self.printer_num), ("type", "=", "toshiba")]
        )
        printer_zebra = self.env["printing.printer"].search(
            [("code", "=", self.printer_num), ("type", "=", "zebra")]
        )

        if not printer_toshiba or not printer_zebra:
            raise UserError(_("Printer not found"))

        picking_id = self.picking_id.id

        # Put in pack
        try:
            # Create a pack for this picking
            box = self.picking_id.put_in_pack()
            if box:
                # Set the number of packages for this picking
                box.nbr_packages = self.nbr_package
        except Exception as e:
            _logger.error(e)
            self.print_passport(picking_id)
            raise UserError(
                _(
                    "Cannot create the package. "
                    "Please give the passport to your manager"
                )
            )

        # Validate the picking
        try:
            self.picking_id.do_new_transfer()
        except Exception as e:
            _logger.error(e)
            self.print_passport(picking_id)
            raise UserError(
                _(
                    "Cannot validate the UOP. "
                    "Please give the passport to your manager"
                )
            )

        # Print labels
        zone_medoc = self.env.ref("__setup__.picking_zone_medicament")
        if self.picking_zone_id == zone_medoc:
            try:
                self.picking_id.print_products_label(printer_id=printer_toshiba.id)
                self.picking_id.print_packages_label(printer_id=printer_zebra.id)
            except Exception as e:
                _logger.error(e)
                self.print_passport(picking_id)
                raise UserError(
                    _(
                        "Cannot print labels. "
                        "Please give the passport to your manager"
                    )
                )

        wizard = self.create({})
        wizard.reload_page()

    def reload_page(self):
        action = self.env.ref("specific_zetes.manage_uop_action").read([])[0]
        action.update({"res_id": self.id})
        return action

    def print_passport(self, picking_id):

        registry = odoo.registry(self._cr.dbname)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            picking = env["stock.picking"].browse(picking_id)

            pick_aliment = env.ref("__setup__.stock_picking_type_ali")
            pick_frigo = env.ref("__setup__.stock_picking_type_froid")

            if picking.picking_type_id == pick_aliment:
                printer_code = constants.PRINTER_ALIMENT
            elif picking.picking_type_id == pick_frigo:
                printer_code = constants.PRINTER_FRIGO
            else:
                printer_code = constants.PRINTER_MEDICAMENT

            printer = env["printing.printer"].search(
                [("code", "=", printer_code), ("type", "=", "pdf")]
            )

            picking.print_passport_report(printer_id=printer.id)


class ManageUOPLine(models.TransientModel):
    _name = "manage.uop.line"

    wizard_id = fields.Many2one("manage.uop", string="Wizard")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        related="pack_op_id.product_id",
        readonly=True,
    )
    pack_op_id = fields.Many2one("stock.pack.operation", "Line", required=True)
    lot_id = fields.Many2one("stock.production.lot", "Lot")
    qty = fields.Integer("Qty", required=True)


class ViewPickingLine(models.TransientModel):
    _name = "view.picking.line"

    wizard_id = fields.Many2one(
        "manage.uop", string="Wizard", readonly=True, required=True
    )
    pack_op_id = fields.Many2one(
        "stock.pack.operation", "Line", required=True, readonly=True
    )
    product_id = fields.Many2one(
        "product.product", "Product", related="pack_op_id.product_id", readonly=True
    )
    lot_id = fields.Many2one("stock.production.lot", "Lot", readonly=True)
    qty_done = fields.Integer("Qty done", readonly=True)
    qty_todo = fields.Integer("Qty todo", readonly=True)

    location_id = fields.Many2one(
        "stock.location",
        string="Location",
        related="pack_op_id.location_id",
        readonly=True,
    )
    location_checksum_right = fields.Char(
        "Location Checksum Right", related="location_id.bin_checksum_1", readonly=True
    )
    location_checksum_left = fields.Char(
        "Location Checksum Left", related="location_id.bin_checksum_2", readonly=True
    )
    lot_checksum = fields.Char("Lot Checksum", related="lot_id.checksum", readonly=True)
    lot_voice_identifier = fields.Char(
        "Lot Voice Identifier", related="lot_id.voice_identifier", readonly=True
    )
