# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models

from ..utils import hw_print


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.multi
    def get_so_partner(self):
        """ Find SO Customer:
            - first find the related move (picking)
            - then find the delivery move (shipping)
            - then find the related procurement
            - then find the originate sales order
            - finally have the customer
        """
        self.ensure_one()
        moves = self.linked_move_operation_ids.mapped("move_id")

        def descend_moves(lvl):
            next_lvl = lvl.mapped("move_dest_id")
            if next_lvl:
                lvl |= descend_moves(next_lvl)
            return lvl

        moves = descend_moves(moves)
        partners = moves.mapped("procurement_id.sale_line_id.order_id.partner_id")
        # While we could potentially have multiple SO, and so partners,
        # practically it won't be the case in 99% otherwise it's not important
        # which one we return
        return partners and partners[0]

    def button_print_product_label(self):
        """
        Using a wrapper to prevent the context from being passed as argument,
        using default arguments instead.
        """
        for pack_operation in self:
            pack_operation.print_product_label()

    @api.multi
    def print_product_label(self, printer_id=False, quantity=1):
        # Product/Customer label
        self.ensure_one()
        if not self.picking_id.partner_id:
            raise Warning(_("No destination partner defined"))
        qty = self.product_id.number_labels_to_print * quantity
        if qty:
            report = "specific_print.report_stock_product_label"
            hw_print(self, report, printer_id=printer_id, qty=qty)

    def button_print_product_product_label(self):
        """
        Using a wrapper to prevent the context from being passed as argument,
        using default arguments instead.
        """
        self.print_product_product_label()

    @api.multi
    def print_product_product_label(self, printer_id=False, quantity=1):
        self.product_id.print_product_label(quantity, printer_id)

    @api.multi
    def get_qty_by_lot(self):
        """
        This method will return the quantity by lot.
        If the product is not track by lot
        we return the quantity done without lot
        :return:
        """
        self.ensure_one()

        if not self.pack_lot_ids:
            return [(int(self.qty_done), None)]

        result = []
        for pack in self.pack_lot_ids:
            result.append((int(pack.qty), pack.lot_id))

        return result

    @api.multi
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
                "specific_print.report_stock_product_food_label",
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
            "id": self.env.ref("specific_print.print_label_action").id,
            "view_mode": "form",
            "res_model": "print.label",
            "target": "new",
            "context": {"default_label_type": "food_product"},
        }
