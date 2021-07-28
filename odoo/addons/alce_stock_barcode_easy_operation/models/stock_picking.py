# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV

import re

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

LOT_BARCODE = re.compile(r"#(?P<product_default_code>\w+)#(?P<lot_name>\w+)#?")


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "barcodes.barcode_events_mixin"]

    def _barcode_process_alldone(self):
        """ Mark all quantities as processed """
        for op in self.pack_operation_product_ids:
            # Force writing in DB
            op.write({"qty_done": op.product_qty})
            for oplot in op.pack_lot_ids:
                oplot.write({"qty": oplot.qty_todo})
            # Now update the UI
            op.qty_done = op.product_qty

    def _barcode_process_lot(self, product_default_code, lot_name):
        lot = self.env["stock.production.lot"].search(
            [
                ("product_id.default_code", "=", product_default_code),
                ("name", "=", lot_name),
            ],
            limit=1,
        )
        if not lot:
            return {
                "warning": {
                    "title": _("Wrong lot"),
                    "message": _("No match for lot %s product %s")
                    % (lot_name, product_default_code),
                }
            }
        op = self.pack_operation_product_ids.filtered(
            lambda r: r.product_id == lot.product_id
            and not r.result_package_id
            and not r.location_processed
        )
        if not op:
            return {
                "warning": {
                    "title": _("Wrong lot"),
                    "message": _("No operation matched for product %s")
                    % product_default_code,
                }
            }
        oplot = op.pack_lot_ids.filtered(lambda r: r.lot_id == lot)
        if not oplot:
            return {
                "warning": {
                    "title": _("Wrong lot"),
                    "message": _("Operation with product %s does not accept lot %s")
                    % (product_default_code, lot_name),
                }
            }
        qty_done = op.qty_done
        new_qty = qty_done + 1
        if (
            float_compare(
                new_qty,
                op.product_qty,
                precision_digits=op._fields["qty_done"].digits[1],
            )
            > 0
        ):
            return {
                "warning": {
                    "title": _("Expected quantity exceeded"),
                    "message": _(
                        "Too much product scanned for operation with product %s.\n"
                        "Expected %s."
                    )
                    % (product_default_code, op.product_qty),
                }
            }
        new_lot_qty = oplot.qty + 1
        if (
            float_compare(
                new_lot_qty,
                oplot.qty_todo,
                precision_digits=oplot._fields["qty"].digits[1],
            )
            > 0
        ):
            remaining_pack_lot_ids = op.pack_lot_ids.filtered(
                lambda a: a.qty < a.qty_todo
            )
            remaining_lot_names = u", ".join(
                remaining_pack_lot_ids.mapped("lot_id.name")
            )
            return {
                "warning": {
                    "title": _("Expected lot quantity exceeded"),
                    "message": _(
                        "Too much lot %s scanned for operation with product %s.\n"
                        "Expected %s lot %s\n"
                        "Remaining lot(s) to scan: %s"
                    )
                    % (
                        lot_name,
                        product_default_code,
                        op.product_qty,
                        lot_name,
                        remaining_lot_names,
                    ),
                }
            }

        # Force writing in DB
        op.write({"qty_done": new_qty})
        oplot.write({"qty": new_lot_qty})
        # Now update the UI
        op.qty_done = qty_done + 1
        return None

    def _barcode_process_product(self, product):
        op = self.pack_operation_product_ids.filtered(
            lambda r: r.product_id.id == product.id
            and not r.result_package_id
            and not r.location_processed
        )
        if not op:
            return {
                "warning": {
                    "title": _("Wrong product"),
                    "message": _("No operation matched for product %s")
                    % product.default_code,
                }
            }
        if op.pack_lot_ids:
            return {
                "warning": {
                    "title": _("Lot required"),
                    "message": _("Operation with product %s need a lot")
                    % product.default_code,
                }
            }
        qty_done = op.qty_done
        new_qty = qty_done + 1
        if (
            float_compare(
                new_qty,
                op.product_qty,
                precision_digits=op._fields["qty_done"].digits[1],
            )
            > 0
        ):
            return {
                "warning": {
                    "title": _("Expected quantity exceeded"),
                    "message": _(
                        "Too much product scanned for operation with product %s.\n"
                        "Expected %s."
                    )
                    % (product.default_code, op.product_qty),
                }
            }
        # Force writing in DB
        op.write({"qty_done": new_qty})
        # Now update the UI
        op.qty_done = qty_done + 1
        return None

    def on_barcode_scanned(self, barcode):
        """ Increase the product or lot quantity of a pack operation.
        Note: self is not an instance of the visible picking. We can only act
        like an onchange on the UI. As the lot is not on the UI, changing it's
        value must be done in DB. However, the total is show on the UI, so we
        need to update it also. As we force changes in DB, saving or discarding
        changes on the UI does not make any difference.
        """
        picking = self.search([("name", "=", self.name)])
        if not picking:
            return UserError(_("Invalid document reference"))
        # Check if command 'alldone'
        if barcode == "C#ALLDONE":
            return self._barcode_process_alldone()
        product_default_code = barcode
        lot_name = None
        # Check if lot: #product#lot or #product#lot#
        m = LOT_BARCODE.match(barcode)
        if m and len(m.groups()) == 2:
            product_default_code = m.group("product_default_code")
            lot_name = m.group("lot_name")
        # ckeck if ZETES code: S-product_code-lot_name-date...
        if barcode.startswith("S-"):
            parts = barcode.split("-")
            product_default_code = parts[1]
            lot_name = parts[2].strip()
        if lot_name:
            return self._barcode_process_lot(product_default_code, lot_name)
        # Check product
        product = self.env["product.product"].search(
            [("default_code", "=", product_default_code)], limit=1
        )
        if product:
            return self._barcode_process_product(product)
        # package
        # Logic for packages in source location
        if self.pack_operation_pack_ids:
            package_source = self.env["stock.quant.package"].search(
                [
                    ("name", "=", barcode),
                    ("location_id", "child_of", self.location_id.id),
                ],
                limit=1,
            )
            if package_source:
                if self._check_source_package(package_source):
                    return None

        # Raise error
        return {
            "warning": {"title": _("Unsupported code"), "message": _("%s") % barcode}
        }
