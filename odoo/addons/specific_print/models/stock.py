# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def hw_print(self, report_xmlid, printer_id=False, qty=1):
    document = self.env["report"]._get_raw(self._ids, report_xmlid, qty=qty)
    report = self.env.ref(report_xmlid)
    behaviour = report.behaviour()[report.id]
    printer = False
    if printer_id:
        printer = self.env["printing.printer"].browse(printer_id)
    if not printer:
        printer = behaviour["printer"]
    if not printer:
        raise UserError(_("No printer assigned"))
    try:
        printer.print_document(report, document, "text")
    except UnicodeEncodeError:
        raise
    except Exception as e:
        _logger.exception("Printer unavailable")
        raise UserError(_("Printer unavailable : %s") % str(e))


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
        self.print_product_label()

    @api.multi
    def print_product_label(self, printer_id=False, quantity=1):
        for op in self:
            if not op.picking_id.partner_id:
                raise Warning(_("No destination partner defined"))
        hw_print(
            self,
            "specific_print.report_stock_product_label",
            printer_id=printer_id,
            qty=quantity,
        )

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


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def print_products_label(self, printer_id=False, quantity=1):
        self.ensure_one()
        if self.partner_id and (
            self.partner_id.no_labels_products or self.customer_id.is_b2c_customer
        ):
            return

        packs_to_print = self.pack_operation_ids.filtered(
            lambda pack_op: not pack_op.product_id.is_do_not_print_label
        )
        if packs_to_print:
            packs_to_print.print_product_label(printer_id=printer_id, quantity=quantity)

    @api.multi
    def print_packages_label(self, quantity=1, printer_id=False):
        self.ensure_one()
        if not self.partner_id:
            raise Warning(_("No destination partner defined"))
        hw_print(
            self,
            "specific_print.report_stock_pick_packs_label",
            printer_id=printer_id,
            qty=quantity,
        )

    @api.multi
    def print_passport_report(self, printer_id):
        self.ensure_one()
        pdf = self.env["report"].get_pdf(self.ids, "specific_report.report_passport")
        printer = self.env["printing.printer"].browse(printer_id)
        printer.print_document("", pdf, "")

    @api.multi
    def print_labels_report(self):
        self.ensure_one()
        if self.partner_id and self.partner_id.no_labels_products:
            raise UserError(_("Customer does not need product labels"))
        return {
            "name": "Print label",
            "type": "ir.actions.act_window",
            "id": self.env.ref("specific_print.print_label_action").id,
            "view_mode": "form",
            "res_model": "print.label",
            "target": "new",
            # sending of all context causes errors
            "context": {"default_label_type": "product"},
        }


class StockPackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"

    @api.multi
    def print_lot_label(self, quantity=1):
        self.ensure_one()
        self.lot_id.print_lot_label()


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.multi
    def print_lot_label(self, quantity=1, printer_id=False):
        self.ensure_one()
        hw_print(
            self, "specific_print.report_lot_label", qty=quantity, printer_id=printer_id
        )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def print_product_label(self, quantity=1, printer_id=False):
        self.ensure_one()
        hw_print(
            self,
            "specific_print.report_lot_nolot_label",
            qty=quantity,
            printer_id=printer_id,
        )
