# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def print_products_label(self, printer_id=False, quantity=1, packages=None):
        self.ensure_one()
        if self.partner_id and (
            self.partner_id.no_labels_products or self.customer_id.is_b2c_customer
        ):
            return

        packs_to_print = self.move_line_ids.filtered(
            lambda ml: ml.product_id.number_labels_to_print
        )
        if packages:
            packs_to_print = packs_to_print.filtered(
                lambda ml, packages=packages: ml.result_package_id in packages
            )
        for pack_to_print in packs_to_print:
            pack_to_print.print_product_label(printer_id=printer_id, quantity=quantity)

    def print_food_products_label(
        self, printer_id=False, quantity=1, packages=None, operations=None
    ):
        self.ensure_one()
        if not self.partner_id:
            raise Warning(_("No destination partner defined"))
        packs_to_print = operations or self.move_line_ids.filtered(
            lambda ml: ml.product_id.number_labels_to_print
        )
        if packages:
            packs_to_print = packs_to_print.filtered(
                lambda ml, packages=packages: ml.result_package_id in packages
            )
        do_not_print_food_labels = self.partner_id.no_labels_food_products
        if packs_to_print:
            if do_not_print_food_labels:
                # We call the print, we need just one label in force printing
                # We don't need lot or anything
                packs_to_print[0].print_food_product_label(
                    printer_id=printer_id,
                    do_not_print_food_labels=do_not_print_food_labels,
                )
            else:
                for pack in packs_to_print:
                    if pack.lot_id:
                        pack.print_food_product_label(
                            printer_id=printer_id,
                            quantity=quantity,
                            quantity_done=pack.qty_done,
                            lot_id=pack.lot_id,
                        )
                    else:
                        pack.print_food_product_label(
                            printer_id=printer_id,
                            quantity=quantity,
                            quantity_done=pack.qty_done,
                        )

    def print_labels_report(self):
        self.ensure_one()
        if self.partner_id and self.partner_id.no_labels_products:
            raise UserError(_("Customer does not need product labels"))
        return {
            "name": "Print label",
            "type": "ir.actions.act_window",
            "id": self.env.ref("alc_label_printing_base.print_label_action").id,
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
            "id": self.env.ref("alc_label_printing_base.print_label_action").id,
            "view_mode": "form",
            "res_model": "print.label",
            "target": "new",
            "context": {"default_label_type": "food_product"},
        }

    def button_print_product_product_label(self):
        """
        Using a wrapper to prevent the context from being passed as argument,.

        using default arguments instead.
        """
        self.ensure_one()
        self.print_product_product_label()

    def print_product_product_label(self, printer_id=False, quantity=1):
        for ml in self.move_line_ids:
            ml.product_id.print_product_label(quantity, printer_id)
