# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, exceptions
from odoo.tools.float_utils import float_compare, float_is_zero

from odoo.addons.component.core import Component


class ChangePackageLot(Component):
    """Provide methods for changing a package or a lot on a move line"""

    _name = "shopfloor.change.package.lot.action"
    _inherit = "shopfloor.process.action"
    _usage = "change.package.lot"

    def change_lot(
        self, pack_operation, old_lot, new_lot, response_ok_func, response_error_func
    ):
        """Change the lot on the move line.

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
            pack_operation, old_lot, new_lot, response_ok_func, response_error_func
        )

    def _change_pack_lot_change_lot(
        self, pack_operation, old_lot, new_lot, response_ok_func, response_error_func
    ):
        def is_lesser(value, other, rounding):
            return float_compare(value, other, precision_rounding=rounding) == -1

        inventory = self._actions_for("inventory")
        product = pack_operation.product_id
        if new_lot.product_id != product:
            return response_error_func(
                pack_operation,
                message=self.msg_store.lot_on_wrong_product(new_lot.name),
            )
        previous_lot = old_lot

        # Changing the lot on the move line updates the reservation on the quants

        message_parts = []

        values = {"lot_id": new_lot.id}

        available_quantity = self.env["stock.quant"]._get_available_quantity(
            product, pack_operation.location_id, lot_id=new_lot, strict=True
        )

        if pack_operation.package_id:
            # TODO ?????
            # pack_operation.package_level_id.explode_package()
            values["package_id"] = False

        to_assign_moves = self.env["stock.move"]
        if float_is_zero(
            available_quantity, precision_rounding=product.uom_id.rounding
        ):
            quants = self.env["stock.quant"]._gather(
                product, pack_operation.location_id, lot_id=new_lot, strict=True
            )
            if quants:
                # we have quants but they are all reserved by other lines:
                # unreserve the other lines and reserve them again after
                unreservable_lines = self.env["stock.pack.operation"].search(
                    [
                        ("lot_id", "=", new_lot.id),
                        ("product_id", "=", product.id),
                        ("location_id", "=", pack_operation.location_id.id),
                        ("qty_done", "=", 0),
                    ]
                )
                if not unreservable_lines:
                    return response_error_func(
                        pack_operation,
                        message=self.msg_store.cannot_change_lot_already_picked(
                            new_lot
                        ),
                    )
                available_quantity = sum(unreservable_lines.mapped("product_qty"))
                to_assign_moves = unreservable_lines.move_id
                # if we leave the package level, it will try to reserve the same
                # one again
                unreservable_lines.package_level_id.explode_package()
                # unreserve qties of other lines
                unreservable_lines.unlink()
            else:
                # * we have *no* quant:
                # The lot is not found at all, but the user scanned it, which means
                # it's an error in the stock data! To allow the user to continue,
                # we post an inventory to add the missing quantity, and a second
                # draft inventory to check later
                inventory.create_stock_correction(
                    pack_operation.move_id,
                    pack_operation.location_id,
                    self.env["stock.quant.package"].browse(),
                    new_lot,
                    pack_operation.product_qty,
                )
                inventory.create_control_stock(
                    pack_operation.location_id,
                    pack_operation.product_id,
                    pack_operation.package_id,
                    pack_operation.lot_id,
                    _("Pick: stock issue on lot: {} found in {}").format(
                        new_lot.name, pack_operation.location_id.name
                    ),
                )
                message_parts.append(
                    _("A draft inventory has been created for control.")
                )

        # re-evaluate float_is_zero because we may have changed available_quantity
        if not float_is_zero(
            available_quantity, precision_rounding=product.uom_id.rounding
        ) and is_lesser(
            available_quantity, pack_operation.product_qty, product.uom_id.rounding
        ):
            new_uom_qty = product.uom_id._compute_quantity(
                available_quantity,
                pack_operation.product_uom_id,
                rounding_method="HALF-UP",
            )
            values["product_uom_qty"] = new_uom_qty

        pack_operation.write(values)

        if "product_uom_qty" in values:
            # when we change the quantity of the move, the state
            # will still be "assigned" and be skipped by "_action_assign",
            # recompute the state to be "partially_available"
            pack_operation.move_id._recompute_state()

        # if the new package has less quantities, assign will create new move
        # lines
        pack_operation.move_id._action_assign()

        # Find other available goods for the lines which were using the
        # lot before...
        to_assign_moves._action_assign()

        message = self.msg_store.lot_replaced_by_lot(previous_lot, new_lot)
        if message_parts:
            message["body"] = "{} {}".format(message["body"], " ".join(message_parts))
        return response_ok_func(pack_operation, message=message)

    def _package_content_replacement_allowed(self, package, pack_operation):
        # we can't replace by a package which doesn't contain the product...
        return pack_operation.product_id in package.quant_ids.product_id

    def change_package(
        self, pack_operation, package, response_ok_func, response_error_func
    ):
        # Prevent change if package is already set and it's the same
        if pack_operation.package_id == package:
            return response_error_func(
                pack_operation,
                message=self.msg_store.package_change_error_same_package(package),
            )

        # prevent to replace a package by a package that would not satisfy the
        # move (different product)
        content_replacement_allowed = self._package_content_replacement_allowed(
            package, pack_operation
        )
        if not content_replacement_allowed:
            return response_error_func(
                pack_operation,
                message=self.msg_store.package_different_content(package),
            )

        previous_package = pack_operation.package_id

        # /!\ be sure to box the side-effects before calling "replace_package"
        # in the savepoint, as we catch the error, we must be sure that any
        # change is rollbacked
        try:
            with self.env.cr.savepoint():
                # if no quantity is available in the package, this call will
                # raise a UserError, which will revert the savepoint
                pack_operation.replace_package(package)
        except exceptions.UserError as err:
            return response_error_func(
                pack_operation,
                message=self.msg_store.package_change_error(package, err.name),
            )

        if previous_package:
            message = self.msg_store.package_replaced_by_package(
                previous_package, package
            )
        else:
            message = self.msg_store.units_replaced_by_package(package)
        return response_ok_func(pack_operation, message=message)
