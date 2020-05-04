# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import _, models
from odoo.exceptions import UserError

lot_barcode = re.compile(r"#(\w+)#(\w+)#?")


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

    def _barcode_process_lot(self, m):
        lot = self.env["stock.production.lot"].search(
            [("product_id.default_code", "=", m.group(1)), ("name", "=", m.group(2))],
            limit=1,
        )
        if not lot:
            return {
                "warning": {
                    "title": _("Wrong lot"),
                    "message": _("No match for lot %s product %s") % m.groups(),
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
                    "message": _("No operation matched for product %s") % m.group(1),
                }
            }
        oplot = op.pack_lot_ids.filtered(lambda r: r.lot_id == lot)
        if not oplot:
            return {
                "warning": {
                    "title": _("Wrong lot"),
                    "message": _("Operation with product %s does not accept lot %s")
                    % m.groups(),
                }
            }
        qty_done = op.qty_done
        # Force writing in DB
        op.write({"qty_done": qty_done + 1})
        oplot.write({"qty": oplot.qty + 1})
        # Now update the UI
        op.qty_done = qty_done + 1

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
        # Force writing in DB
        op.write({"qty_done": qty_done + 1})
        # Now update the UI
        op.qty_done = qty_done + 1

    def on_barcode_scanned(self, barcode):
        """ Increase the product or lot quantity of a pack operation.
        Note: self is not an instance of the visible picking. We can only act
        like an onchange on the UI. As the lot is not on the UI, changing it's
        value must be done in DB. However, the total is show on the UI, so we
        need to update it also. As we force changes in DB, saving or discarding
        changes on the UI does not make any difference.
        """
        if not self.operator_id:
            raise UserError(_("Please start operation first"))

        picking = self.search([("name", "=", self.name)])
        if not picking:
            return UserError(_("Invalid document reference"))
        # Check if command 'alldone'
        if barcode == "C#ALLDONE":
            return self._barcode_process_alldone()
        # Check if lot: #product#lot or #product#lot#
        m = lot_barcode.match(barcode)
        if m and len(m.groups()) == 2:
            return self._barcode_process_lot(m)
        # Check product
        product = self.env["product.product"].search(
            [("default_code", "=", barcode)], limit=1
        )
        if product:
            return self._barcode_process_product(product)
        # Raise error
        return {
            "warning": {"title": _("Unsupported code"), "message": _("%s") % barcode}
        }
