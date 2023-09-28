# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _

from odoo.addons.alc_printing_base.utils import hw_print
from odoo.addons.stock.models.stock_move_line import StockMoveLine as MoveLine


class StockMoveLine(MoveLine):
    def get_so_partner(self):
        """Find SO Customer:

        - first find the related move (picking)
        - then find the delivery move (shipping)
        - then find the related procurement
        - then find the originate sales order
        - finally have the customer
        """
        self.ensure_one()
        moves = self.move_id.move_dest_ids

        def descend_moves(lvl):
            next_lvl = lvl.mapped("move_dest_ids")
            if next_lvl:
                lvl |= descend_moves(next_lvl)
            return lvl

        moves = descend_moves(moves)
        partners = moves.mapped("sale_line_id.order_id.partner_id")
        # While we could potentially have multiple SO, and so partners,
        # practically it won't be the case in 99% otherwise it's not important
        # which one we return
        return partners and partners[0]

    def button_print_product_label(self):
        """
        Using a wrapper to prevent the context from being passed as argument,.

        using default arguments instead.
        """
        for move_line in self:
            move_line.print_product_label()

    def print_product_label(self, printer_id=False, quantity=1):
        # Product/Customer label
        self.ensure_one()
        if not self.picking_id.partner_id:
            raise Warning(_("No destination partner defined"))
        qty = self.product_id.number_labels_to_print * quantity
        if qty:
            report = "alc_product_label_printing.report_stock_product_label"
            hw_print(self, report, printer_id=printer_id, qty=qty)

    def button_print_product_product_label(self):
        """
        Using a wrapper to prevent the context from being passed as argument,.

        using default arguments instead.
        """
        self.print_product_product_label()

    def print_product_product_label(self, printer_id=False, quantity=1):
        self.product_id.print_product_label(quantity, printer_id)

    def get_qty_by_lot(self):
        """
        This method will return the quantity by lot.

        If the product is not track by lot
        we return the quantity done without lot
        """
        self.ensure_one()
        return [(int(self.qty_done), self.lot_id if self.lot_id else None)]

    def print_food_product_label(
        self,
        quantity=1,
        printer_id=False,
        lot_id=None,
        quantity_done=1,
        do_not_print_food_labels=False,
    ):
        # Product/Customer label
        self.ensure_one()
        qty = quantity * self.product_id.number_labels_to_print

        if do_not_print_food_labels:
            # If we arrive here by another entry point than cluster picking
            # scan destination flow, this means we specifically required the print.
            # In that case, we want only one label
            qty = 1
            quantity_done = 1

        if qty:
            hw_print(
                self,
                "alc_product_label_printing.report_stock_product_food_label",
                qty=qty,
                printer_id=printer_id,
                lot_id=lot_id,
                qty_done=quantity_done,
            )

    def print_food_report(self):
        self.ensure_one()
        return {
            "name": "Print food label",
            "type": "ir.actions.act_window",
            "id": self.env.ref("alc_label_printing_base.print_label_action").id,
            "view_mode": "form",
            "res_model": "print.label",
            "target": "new",
            "context": {"default_label_type": "food_product"},
        }

    def print_lot_label(self, quantity=1, printer_id=None):
        self.ensure_one()
        self.lot_id.print_lot_label(quantity=quantity, printer_id=printer_id)

    def stock_move_line_action(self):
        action_xml_id = "alc_product_label_printing.stock_move_line_action"
        window_action = self.env.ref(action_xml_id).read()[0]
        window_action["res_id"] = self.id
        return window_action
