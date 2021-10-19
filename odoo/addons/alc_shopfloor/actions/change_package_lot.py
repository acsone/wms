# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools.float_utils import float_compare

from odoo.addons.component.core import Component


class ChangePackageLot(Component):
    """Provide methods for changing a package or a lot on a pack operation"""

    _name = "shopfloor.change.package.lot.action"
    _inherit = "shopfloor.process.action"
    _usage = "change.package.lot"

    def change_lot(
        self,
        pack_operation,
        previous_lot,
        new_lot,
        response_ok_func,
        response_error_func,
    ):
        """Change the lot on the pack operation.

        :param response_ok_func: callable used to return ok response
        :param response_error_func: callable used to return error response
        """
        # If the lot is part of a package, what we really want
        # is not to change the lot, but change the package (which will
        # in turn change the lot altogether), but we have to pay attention
        # to some things:
        # * cannot replace a package by a lot without package (qty may be
        #   different, ...)
        # * if we have several packages for the same lot, we can't know which
        #   one the operator is moving, ask to scan a package
        lot_quants = self.env["stock.quant"].search(
            [
                ("lot_id", "=", new_lot.id),
                ("location_id", "=", pack_operation.location_id.id),
                ("qty", ">", 0),
            ]
        )
        package_quants = lot_quants.filtered(lambda quant: quant.package_id)
        unit_quants = lot_quants - package_quants

        if len(package_quants) > 1 or (package_quants and unit_quants):
            # When we can't know which package to take, ask to scan a package.
            # If we have both units and package, they have to scan the package
            # first.
            return response_error_func(
                pack_operation,
                message=self.msg_store.several_packs_in_location(
                    pack_operation.location_id
                ),
            )
        if len(package_quants) == 1:
            # change the package directly
            package = package_quants.package_id
            return self.change_package(
                pack_operation, package, response_ok_func, response_error_func
            )
        return self._change_pack_lot_change_lot(
            pack_operation, previous_lot, new_lot, response_ok_func, response_error_func
        )

    def _change_pack_lot_change_lot(
        self,
        pack_operation,
        previous_lot,
        new_lot,
        response_ok_func,
        response_error_func,
    ):
        product = pack_operation.product_id
        if new_lot.product_id != product:
            return response_error_func(
                pack_operation,
                message=self.msg_store.lot_on_wrong_product(new_lot.name),
            )

        previous_pack_lot = pack_operation.pack_lot_ids.filtered(
            lambda a, lot=previous_lot: a.lot_id == lot
        )
        new_pack_lot = pack_operation.pack_lot_ids.filtered(
            lambda a, lot=new_lot: a.lot_id == lot and not a.qty
        )
        previous_qty_done = sum(previous_pack_lot.mapped("qty"))
        previous_qty_todo = sum(previous_pack_lot.mapped("qty_todo"))
        previous_remaining_qty = previous_qty_todo - previous_qty_done
        if new_pack_lot:
            qty_todo = new_pack_lot.qty_todo + previous_remaining_qty
            new_pack_lot.write({"qty_todo": qty_todo})
            if (
                float_compare(
                    previous_qty_done, 0, precision_rounding=product.uom_id.rounding
                )
                > 0
            ):
                previous_pack_lot.write({"qty_todo": previous_qty_done})
            else:
                previous_pack_lot.unlink()
        else:
            if (
                float_compare(
                    previous_qty_done, 0, precision_rounding=product.uom_id.rounding
                )
                > 0
            ):
                new_line, _qty_check = pack_operation._split_qty_to_be_done(
                    previous_qty_done, lot_id=previous_lot
                )
                new_line.lot_id = new_lot
            else:
                previous_pack_lot.lot_id = new_lot

        message = self.msg_store.lot_replaced_by_lot(previous_lot, new_lot)
        return response_ok_func(pack_operation, message=message, force_lot=new_lot)

    def _package_content_replacement_allowed(self, package, pack_operation):
        # we can't replace by a package which doesn't contain the product...
        return pack_operation.product_id in package.quant_ids.product_id

    def change_package(
        self, pack_operation, package, response_ok_func, response_error_func
    ):
        raise SystemError("Change packge not implemented")
