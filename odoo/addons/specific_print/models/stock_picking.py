# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..utils import hw_print


class StockPicking(models.Model):
    _inherit = "stock.picking"

    checksum = fields.Char("Checksum", copy=False)

    @api.multi
    def print_products_label(self, printer_id=False, quantity=1, packages=None):
        self.ensure_one()
        if self.partner_id and (
            self.partner_id.no_labels_products or self.customer_id.is_b2c_customer
        ):
            return

        packs_to_print = self.pack_operation_ids.filtered(
            lambda pack_op: pack_op.product_id.number_labels_to_print
        )
        if packages:
            packs_to_print = packs_to_print.filtered(
                lambda pack_op, packages=packages: pack_op.result_package_id in packages
            )
        for pack_to_print in packs_to_print:
            pack_to_print.print_product_label(printer_id=printer_id, quantity=quantity)

    @api.multi
    def print_food_products_label(
        self, printer_id=False, quantity=1, packages=None, operations=None
    ):
        self.ensure_one()
        if not self.partner_id:
            raise Warning(_("No destination partner defined"))

        packs_to_print = operations or self.pack_operation_ids.filtered(
            lambda pack_op: pack_op.product_id.number_labels_to_print
        )
        if packages:
            packs_to_print = packs_to_print.filtered(
                lambda pack_op, packages=packages: pack_op.result_package_id in packages
            )
        if packs_to_print:
            for pack in packs_to_print:
                if pack.pack_lot_ids:
                    for pack_lot in pack.pack_lot_ids:
                        pack.print_food_product_label(
                            printer_id=printer_id,
                            quantity=quantity,
                            lot_id=pack_lot.lot_id,
                        )
                else:
                    pack.print_food_product_label(
                        printer_id=printer_id, quantity=quantity
                    )

    @api.multi
    def print_packages_label(self, quantity=1, printer_id=False, packages=None):
        self.ensure_one()
        if not self.partner_id:
            raise Warning(_("No destination partner defined"))
        hw_print(
            self,
            "specific_print.report_stock_pick_packs_label",
            printer_id=printer_id,
            qty=quantity,  # not affected by number_labels_to_print
            packages_only=packages,
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
