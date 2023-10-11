# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV

import re

from odoo import _
from odoo.exceptions import UserError
from odoo.tools import float_compare

from odoo.addons.barcodes.models.barcode_events_mixin import BarcodeEventsMixin
from odoo.addons.stock_barcode.models import stock_picking

LOT_BARCODE = re.compile(r"#(?P<product_default_code>\w+)#(?P<lot_name>\w+)#?")


class StockPicking(stock_picking.StockPicking, BarcodeEventsMixin):

    _name = "stock.picking"

    def _barcode_process_alldone(self):
        """Mark all quantities as processed."""
        for op in self.move_line_ids:
            # Force writing in DB
            op.write({"qty_done": op.reserved_uom_qty})
            # Now update the UI
            op.qty_done = op.reserved_uom_qty

    def _barcode_process_lot(self, product_default_code, lot_name):
        lot = self.env["stock.lot"].search(
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
                    "message": _(
                        "No match for lot %(lot)s product %(product)s.",
                        lot=lot_name,
                        product=product_default_code,
                    ),
                }
            }
        op = self.move_line_ids.filtered(
            lambda r: r.product_id == lot.product_id and not r.result_package_id
        )
        if not op:
            return {
                "warning": {
                    "title": _("Wrong lot"),
                    "message": _(
                        "No operation matched for product %(product)s.",
                        product=product_default_code,
                    ),
                }
            }
        ml = op.filtered(lambda x: x.lot_id == lot)
        if not ml:
            return {
                "warning": {
                    "title": _("Wrong lot"),
                    "message": _(
                        "Operation with product %(product)s does not accept lot "
                        "%(lot)s.",
                        product=product_default_code,
                        lot=lot_name,
                    ),
                }
            }
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        qty_done = ml.qty_done
        new_qty = qty_done + 1
        if float_compare(new_qty, ml.reserved_uom_qty, precision_digits=precision) > 0:
            return {
                "warning": {
                    "title": _("Expected quantity exceeded"),
                    "message": _(
                        "Too much product scanned for operation with product "
                        "%(product)s.\nExpected %(qty)s.",
                        product=product_default_code,
                        qty=ml.reserved_uom_qty,
                    ),
                }
            }
        if float_compare(new_qty, lot.product_qty, precision_digits=precision) > 0:
            return {
                "warning": {
                    "title": _("Expected lot quantity exceeded"),
                    "message": _(
                        "Too much product %(product)s scanned for operation with lot "
                        "%(lot)s.\n"
                        "Expected quantity for this lot is: %(qty)s.",
                        product=product_default_code,
                        lot=lot_name,
                        qty=lot.product_qty,
                    ),
                }
            }

        # Force writing in DB
        ml.write({"qty_done": new_qty})
        # Now update the UI
        ml.qty_done = qty_done + 1
        return None

    def _barcode_process_product(self, product):
        op = self.move_line_ids.filtered(
            lambda r: r.product_id.id == product.id and not r.result_package_id
        )
        if not op:
            return {
                "warning": {
                    "title": _("Wrong product"),
                    "message": _(
                        "No operation matched for product %(product)s.",
                        product=product.default_code,
                    ),
                }
            }
        if product.tracking == "lot":
            return {
                "warning": {
                    "title": _("Lot required"),
                    "message": _(
                        "Operation with product %(product)s needs a lot.",
                        product=product.default_code,
                    ),
                }
            }
        qty_done = op.qty_done
        new_qty = qty_done + 1
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if (
            float_compare(
                new_qty,
                op.reserved_uom_qty,
                precision_digits=precision,
            )
            > 0
        ):
            return {
                "warning": {
                    "title": _("Expected quantity exceeded"),
                    "message": _(
                        "Too much product scanned for operation with product "
                        "%(product)s.\nExpected %(qty)s.",
                        product=product.default_code,
                        qty=op.reserved_uom_qty,
                    ),
                }
            }
        # Force writing in DB
        op.write({"qty_done": new_qty})
        # Now update the UI
        op.qty_done = qty_done + 1
        return None

    def on_barcode_scanned(self, barcode):
        """Increase the product or lot quantity of a pack operation.

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
        if self.move_line_ids:
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
            "warning": {
                "title": _("Unsupported code"),
                "message": _("%(barcode)s", barcode=barcode),
            }
        }
