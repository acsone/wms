# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import OrderedDict

from odoo import _

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component

from ..utils import to_float

# NOTE for the implementation: share several similarities with the "cluster
# picking" scenario


# TODO add picking and package content in package level?


class LocationContentTransfer(Component):
    """
    Methods for the Location Content Transfer Process

    Move the full content of a location to one or another location.

    Generally used to move a pallet with multiple boxes to either:

    * 1 destination location, unloading the full pallet
    * To multiple destination locations, unloading one product/lot per
      locations
    * To multiple destination locations, unloading one product/lot per
      locations and then unloading all remaining product/lot to a single final
      destination

    The pack operations must exist beforehand, the workflow only moves them.

    Expected:

    * All the pack operations have a destination set, and are done.

    2 complementary actions are possible on the screens allowing to do an operation:

    * Declare a stock out for a product or package (nothing found in the
      location)
    * Skip to the next operation (will be asked again at the end)

    Flow Diagram: https://www.draw.io/#G1qRenBcezk50ggIazDuu2qOfkTsoIAxXP
    """

    _inherit = "base.shopfloor.process"
    _name = "shopfloor.location.content.transfer"
    _usage = "location_content_transfer"
    _description = __doc__

    ############
    # SERVICES #
    ############

    def start_or_recover(self):
        """ Start a new session or recover an existing one

        If the current user had transfers in progress in this scenario
        and reopen the menu, we want to directly reopen the screens to choose
        destinations. Otherwise, we search for the first stock refill arrange
        with a location with a barcode_picking_type into the list of the
        scenario picking_types. If one is available, we start a picking for
        this location.
        At the end of no operation is created we go to the "start" state
        """
        started_pickings = self._search_recover_pickings()
        if started_pickings:
            return self._router_single_or_all_destination(
                started_pickings, message=self.msg_store.recovered_previous_session()
            )
        refill_arrange = self._refill_arrange_search()
        if refill_arrange:
            return self.scan_location(refill_arrange[0].location_id.barcode)
        return self._response_for_start(
            message=self.msg_store.location_content_transfer_no_work()
        )

    def __start_or_recover(self):
        """Start a new session or recover an existing one

        If the current user had transfers in progress in this scenario
        and reopen the menu, we want to directly reopen the screens to choose
        destinations. Otherwise, we go to the "start" state.
        """
        started_pickings = self._search_recover_pickings()
        if started_pickings:
            return self._router_single_or_all_destination(
                started_pickings, message=self.msg_store.recovered_previous_session()
            )
        return self._response_for_start()

    def scan_location(self, barcode):
        """Scan start location

        Called at the beginning at the workflow to select the location from which
        we want to move the content.

        All the operations must have the same picking type.

        If the scanned location has no operations, new operations to move the
        whole content of the location are created if:

        * the menu has the option "Allow to create move(s)"
        * the menu is linked to only one picking type.

        When operations have different destinations, the
        first operation is sent to the client.

        The selected operations to process are bound to the current operator,
        this will allow another operator to find unprocessed lines in parallel
        and not overlap with current ones.

        Transitions:
        * start: location not found, ...
        * scan_destination_all: if the destination of all the lines and package
        levels have the same destination
        * start_single: if any line or package level has a different destination
        """
        location = self._actions_for("search").location_from_scan(barcode)
        if not location:
            return self._response_for_start(message=self.msg_store.barcode_not_found())
        operations = self._find_location_operations(location)
        pickings = operations.mapped("picking_id")
        picking_types = pickings.mapped("picking_type_id")

        savepoint = self._actions_for("savepoint").new()
        unreserved_moves = self.env["stock.move"].browse()
        if self.work.menu.allow_unreserve_other_moves:
            operations, unreserved_moves, response = self._unreserve_other_operations(
                location, operations
            )
            if response:
                return response
        else:
            if len(picking_types) > 1:
                return self._response_for_start(
                    message={
                        "message_type": "error",
                        "body": _("This location content can't be moved at once."),
                    }
                )
            if picking_types - self.picking_types:
                return self._response_for_start(
                    message={
                        "message_type": "error",
                        "body": _(
                            "This location content can't be moved using this menu."
                        ),
                    }
                )
        # Ensure we process move lines related to pickings having only one source
        # location among all their move lines. If there are different source
        # locations, we put the move lines we are interested in in a separate picking.
        # This is required as we can only deal within this scenario with pickings
        # that share the same source location.
        pickings = operations._split_pickings_from_source_location()

        # If the following criteria are met:
        #   - no operations have been found
        #   - the menu is configured to allow the creation of moves
        #   - the menu is bind to one picking type
        #   - scanned location is a valid source for one the menu's picking types
        # then prepare new stock moves to move goods from the scanned location.
        menu = self.work.menu
        if (
            not operations
            and menu.allow_move_create
            and len(self.picking_types) == 1
            and self.is_src_location_valid(location)
        ):
            new_moves = self._create_moves_from_location(location)
            if not new_moves:
                return self._response_for_start(
                    message=self.msg_store.no_pack_in_location(location)
                )
            new_moves.action_confirm()
            new_moves.action_assign()
            if not all([x.state == "assigned" for x in new_moves]):
                savepoint.rollback()
                return self._response_for_start(
                    message=self.msg_store.new_move_lines_not_assigned()
                )
            pickings = new_moves.mapped("picking_id")
            operations = new_moves.mapped("linked_move_operation_ids.operation_id")
            for operation in operations:
                if not self.is_dest_location_valid(
                    new_moves, operation.location_dest_id
                ):
                    savepoint.rollback()

                    return self._response_for_start(
                        message=self.msg_store.location_content_unable_to_transfer(
                            location
                        )
                    )

        if self.work.menu.ignore_no_putaway_available and self._no_putaway_available(
            operations
        ):
            # the putaway created a move line but no putaway was possible, so revert
            # to the initial state
            savepoint.rollback()
            return self._response_for_start(
                message=self.msg_store.no_putaway_destination_available()
            )

        if not pickings:
            return self._response_for_start(
                message=self.msg_store.location_empty(location)
            )

        for operation in operations:
            operation.qty_done = operation.product_qty
            operation.shopfloor_user_id = self.shopfloor_user.id
            for pack_lot in operation.pack_lot_ids:
                pack_lot.qty = pack_lot.qty_todo

        pickings.write({"operator_id": self.shopfloor_user.id, "printed": True})

        unreserved_moves.action_assign()

        savepoint.release()

        return self._router_single_or_all_destination(pickings)

    def set_destination_all(self, location_id, barcode, confirmation=False):
        """Scan destination location for all the moves of the location

        barcode is a stock.location for the destination

        Transitions:
        * scan_destination_all: invalid destination or could not set moves to done
        * start: moves are done
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        operations = self._find_operations(location)
        pickings = operations.mapped("picking_id")
        if not pickings:
            # if we can't find the lines anymore, they likely have been done
            # by someone else
            return self._response_for_start(message=self.msg_store.already_done())
        scanned_location = self._actions_for("search").location_from_scan(barcode)
        if not scanned_location:
            return self._response_for_scan_destination_all(
                pickings, message=self.msg_store.barcode_not_found()
            )

        moves = operations.mapped("linked_move_operation_ids.move_id")
        if not self.is_dest_location_valid(moves, scanned_location):
            return self._response_for_scan_destination_all(
                pickings, message=self.msg_store.dest_location_not_allowed()
            )
        if not confirmation and self.is_dest_location_to_confirm(
            operations.mapped("location_dest_id"), scanned_location
        ):
            return self._response_for_scan_destination_all(
                pickings, confirmation_required=True
            )
        self._lock_lines(operations)

        self._set_all_destination_operations_and_done(
            pickings, operations, scanned_location
        )

        completion_info = self._actions_for("completion.info")
        completion_info_popup = completion_info.popup(operations)
        return self._response_for_start(
            message=self.msg_store.location_content_transfer_complete(
                location, scanned_location
            ),
            popup=completion_info_popup,
        )

    def go_to_single(self, location_id):
        """Ask the operation

        If the user was brought to the screen allowing to move everything to
        the same location, but they want to move them to different locations,
        this method will return the first operation.

        Transitions:
        * start: no remaining operation to do in the location
        * start_single: if any operation has a different destination
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        operations = self._find_operations(location)
        if not operations:
            return self._response_for_start(
                message=self.msg_store.no_lines_to_process()
            )
        return self._response_for_start_single(operations.mapped("picking_id"))

    def scan_line(self, location_id, operation_id, barcode):
        """Scan a move line to move

        It validates that the user scanned the correct package, lot or product.

        Transitions:
        * start: no remaining lines in the location
        * start_single: barcode not found, ...
        * scan_destination: the barcode matches
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            operations = self._find_operations(location)
            return self._response_for_start_single(
                operations.mapped("picking_id"),
                message=self.msg_store.record_not_found(),
            )

        search = self._actions_for("search")

        package = search.package_from_scan(barcode)
        if package and operation.package_id == package:
            return self._response_for_scan_destination(location, operation)

        product = search.product_from_scan(barcode)
        if product:
            if product == operation.product_id and product.tracking in (
                "lot",
                "serial",
            ):
                operations = self._find_operations(location)
                return self._response_for_start_single(
                    operations.mapped("picking_id"),
                    message=self.msg_store.scan_lot_on_product_tracked_by_lot(),
                )
            if operation.package_id and product in operation.product_ids:
                other_operations = self._find_operations(location) - operation
                if product in other_operations.mapped("product_ids"):
                    # The product has been scanned but we expected a package
                    # When the product exists in other operations as raw products
                    # or part of another package, we can't be sure they scanned
                    # the correct package, so ask to scan the package.
                    operations = self._find_operations(location)
                    return self._response_for_start_single(
                        operations.mapped("picking_id"),
                        message={
                            "message_type": "error",
                            "body": _("Scan the package"),
                        },
                    )
            if product in operation.product_ids:
                return self._response_for_scan_destination(location, operation)

        lot = search.lot_from_scan(barcode, operation)
        if lot:
            if lot in operation.mapped("pack_lot_ids.lot_id"):
                return self._response_for_scan_destination(location, operation)
            if operation.package_id and lot in operation.lot_ids:
                other_operations = self._find_operations(location) - operation
                if lot in other_operations.mapped("lot_ids"):
                    # The lot has been scanned but we expected a package
                    # When the lot exists in other operations
                    # or part of another package, we can't be sure they scanned
                    # the correct package, so ask to scan the package.
                    return self._response_for_start_single(
                        operation.picking_id,
                        message={
                            "message_type": "error",
                            "body": _("Scan the package"),
                        },
                    )
                return self._response_for_scan_destination(location, operation)

        operations = self._find_operations(location)
        return self._response_for_start_single(
            operations.mapped("picking_id"), message=self.msg_store.barcode_not_found()
        )

    def set_destination_line(  # noqa: C901
        self,
        location_id,
        operation_id,
        quantity,
        barcode,
        lot_id=False,
        confirmation=False,
    ):
        """Scan destination location for operation

        If the quantity < qty of the line, split the move and reserve it.
        If the move has other move lines / package levels it has to be split
        so we can post only this part.

        After the destination and quantity are set, the move is set to done.

        Transitions:
        * scan_destination: invalid destination or could not
        * start_single: continue with the next package level / line
        * start: if there is no more package level / line to process
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            operations = self._find_operations(location)
            return self._response_for_start_single(operations.mapped("picking_id"))
        search = self._actions_for("search")
        scanned_location = search.location_from_scan(barcode)
        if not scanned_location:
            return self._response_for_scan_destination(
                location, operation, message=self.msg_store.no_location_found()
            )
        moves = operation.linked_move_operation_ids.mapped("move_id")
        if not self.is_dest_location_valid(moves, scanned_location):
            return self._response_for_scan_destination(
                location, operation, message=self.msg_store.dest_location_not_allowed()
            )
        if not confirmation and self.is_dest_location_to_confirm(
            operation.location_dest_id, scanned_location
        ):
            return self._response_for_scan_destination(
                location, operation, confirmation_required=True
            )
        if operation.pack_lot_ids and not lot_id:
            operations = self._find_operations(location)
            return self._response_for_start_single(
                operations.mapped("picking_id"),
                message=self.msg_store.scan_lot_on_product_tracked_by_lot(),
            )
        if lot_id and lot_id not in operation.pack_lot_ids.mapped("lot_id").ids:
            operations = self._find_operations(location)
            return self._response_for_start_single(
                operations.mapped("picking_id"),
                message=self.msg_store.record_not_found(),
            )
        self._lock_lines(operation)

        qty_todo = operation.product_qty
        pack_lot = self.env["stock.pack.operation.lot"].browse()
        remaining_operation = self.env["stock.pack.operation"].browse()
        if lot_id:
            pack_lot = operation.pack_lot_ids.filtered(
                lambda a, l_id=lot_id: a.lot_id.id == l_id
            )
            qty_todo = sum(operation.pack_lot_ids.mapped("qty_todo"))
        if quantity < qty_todo:
            # Update the current move line quantity and
            # put the scanned qty (the move line) in its own move
            # (by splitting the current one)
            operation.qty_done = quantity
            if pack_lot:
                operation.pack_lot_ids.write({"qty": 0})
                pack_lot.qty = quantity
            # We must first split pack operations and ensure that links are
            # preserved with the original move
            remaining_operation = operation._split_quantities_done_preserve_link()
            remaining_operation.qty_done = remaining_operation.product_qty
            operation.picking_id.recompute_remaining_qty(done_qtys=True)
            # reset qty_done on pack_lot since the UI expect to have qty set to qty_todo
            for _pack_lot in remaining_operation.pack_lot_ids:
                _pack_lot.qty = _pack_lot.qty_todo
            new_moves = self.env["stock.move"].browse()
            # we now must move the current operation into a new move to
            # validate it independently that the remaining operation
            # the remaining operation are preserved into the current move
            for link in operation.linked_move_operation_ids:
                move = link.move_id
                if remaining_operation not in move.pack_operation_ids:
                    continue
                new_moves |= move.split_other_pack_operations(remaining_operation)
                new_moves |= move.split_other_pack_operations(remaining_operation)

        # Ensure that we validate only a move for the current operation.
        # If a move has more than 1 pack operation linked, we must split the
        # move according to the remaining operations when processing the first
        # pack operation
        moves_to_validate_candidate = operation.linked_move_operation_ids.mapped(
            "move_id"
        )
        moves_to_validate_candidate._recompute_state()
        moves_to_validate_ids = []
        for move in moves_to_validate_candidate:
            remaining_operations = move.pack_operation_ids - operation
            if remaining_operations:
                moves_to_validate_ids.append(
                    move.split_other_pack_operations(remaining_operations).id
                )
            else:
                moves_to_validate_ids.append(move.id)
        moves_to_validate = self.env["stock.move"].browse(moves_to_validate_ids)

        self._write_destination_on_operations(operation, scanned_location)
        stock = self._actions_for("stock")
        stock.validate_moves(moves_to_validate)
        if set(
            remaining_operation.linked_move_operation_ids.mapped("move_id.state")
        ) != {"assigned"}:
            remaining_operation.linked_move_operation_ids.mapped(
                "move_id"
            ).action_assign()
        # remaining_operations.linked_move_operation_ids.mapped("move_id").action_assign()
        move_lines = self._find_operations(location)
        message = self.msg_store.location_content_transfer_item_complete(
            scanned_location
        )
        completion_info = self._actions_for("completion.info")
        completion_info_popup = completion_info.popup(operation)
        return self._response_for_start_single(
            move_lines.mapped("picking_id"),
            message=message,
            popup=completion_info_popup,
        )

    def postpone_line(self, location_id, operation_id):
        """Mark a move line as postponed and return the next level/line

        Transitions:
        * start_single: continue with the next package level / line
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        operation = self.env["stock.pack.operation"].browse(operation_id)
        operations = self._find_operations(location)
        if operation.exists():
            pickings = operations.mapped("picking_id")
            sorter = self._actions_for("location_content_transfer.sorter")
            sorter.feed_pickings(pickings)
            operation.shopfloor_postpone(sorter.operations())
        return self._response_for_start_single(operations.mapped("picking_id"))

    def stock_out_line(self, location_id, operation_id, lot_id=None):
        """Declare a stock out on a move line

        It first ensures the stock.move only has this move line. If not, it
        splits the move to have no side-effect on the other package levels/move
        lines.

        It unreserves the move, create an inventory at 0 in the move's source
        location, create a second draft inventory (if none exists) to check later.
        Finally, it cancels the move.

        Transitions:
        * start: no more content to move
        * start_single: continue with the next package level / line
        """
        location = self.env["stock.location"].browse(location_id)
        if not location.exists():
            return self._response_for_start(message=self.msg_store.record_not_found())
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            operations = self._find_operations(location)
            return self._response_for_start_single(operations.mapped("picking_id"))
        if operation.pack_lot_ids and not lot_id:
            operations = self._find_operations(location)
            return self._response_for_start_single(
                operations.mapped("picking_id"),
                message=self.msg_store.scan_lot_on_product_tracked_by_lot(),
            )
        if lot_id and lot_id not in operation.pack_lot_ids.mapped("lot_id").ids:
            operations = self._find_operations(location)
            return self._response_for_start_single(
                operations.mapped("picking_id"),
                message=self.msg_store.record_not_found(),
            )

        inventory = self._actions_for("inventory")
        src_location = operation.location_id
        # if the stockout is for a lot, and the operation is for more than 1
        # lot, we must split the current operation to isolate the current lot
        # in its own operation
        if lot_id and len(operation.pack_lot_ids) > 0:
            operation.pack_lot_ids.write({"qty": 0})
            pack_lot = operation.pack_lot_ids.filtered(
                lambda a, l_id=lot_id: a.lot_id.id == l_id
            )
            pack_lot.qty = pack_lot.qty_todo
            remaining_operation = operation._split_quantities_done_preserve_link()
            remaining_operation.qty_done = remaining_operation.product_qty
            operation.picking_id.recompute_remaining_qty(done_qtys=True)
            # reset qty_done on pack_lot since the UI expect to have qty set to qty_todo
            for pack_lot in remaining_operation.pack_lot_ids:
                pack_lot.qty = pack_lot.qty_todo

        lot = self.env["stock.production.lot"].browse(lot_id)

        moves = operation.linked_move_operation_ids.mapped("move_id")
        # first split other operation
        for link in operation.linked_move_operation_ids:
            move = link.move_id
            move.split_other_pack_operations(operation)

        package = operation.package_id
        moves.do_unreserve()
        moves.mapped("pack_operation_ids").unlink()
        moves._recompute_state()
        for move in moves:
            # Create an inventory at 0 in the move's source location
            inventory.create_stock_issue(move, src_location, package, lot)
            # Create a draft inventory to control stock
            inventory.create_control_stock(src_location, move.product_id, package, lot)
        # no_recompute_pack required by stock_groupbypartner... what a mess
        moves.with_context(no_recompute_pack=True).action_cancel()
        operations = self._find_operations(location)
        return self._response_for_start_single(operations.mapped("picking_id"))

    ##################
    # Helpers methods
    ##################
    def _refill_arrange_search(self):
        RefillArrange = self.env["report.stock.refill.arrange"]
        return RefillArrange.search(
            [
                ("reservation_id", "=", False),
                ("barcode_picking_type_id", "in", self.picking_types.ids),
            ],
            order="refill_priority_arrange desc",
        )

    def _find_location_operations_domain(self, location):
        return [
            ("location_id", "=", location.id),
            ("qty_done", "=", 0),
            ("state", "in", ("assigned", "partially_available")),
            ("shopfloor_user_id", "=", False),
        ]

    def _find_location_all_operations_domain(self, location):
        return [
            ("location_id", "=", location.id),
            ("state", "in", ("assigned", "partially_available")),
        ]

    def _find_location_operations(self, location):
        """Find lines that potentially are to move in the location"""
        return self.env["stock.pack.operation"].search(
            self._find_location_operations_domain(location)
        )

    def _create_moves_from_location(self, location):
        # get all quants from the scanned location
        quants = self.env["stock.quant"].search(
            [("location_id", "=", location.id), ("qty", ">", 0)]
        )
        # create moves for each quant
        picking_type = self.picking_types
        move_ids = []
        qty_by_product_and_uom = OrderedDict()
        for quant in quants:
            key = (quant.product_id, quant.product_uom_id)
            qty_by_product_and_uom[key] = (
                qty_by_product_and_uom.setdefault(key, 0) + quant.qty
            )
        for (product, uom), qty in qty_by_product_and_uom.items():
            move_ids.append(
                self.env["stock.move"]
                .create(
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom": uom.id,
                        "product_uom_qty": qty,
                        "location_id": location.id,
                        "location_dest_id": picking_type.default_location_dest_id.id,
                        "origin": self.work.menu.name,
                        "picking_type_id": picking_type.id,
                    }
                )
                .id
            )
        return self.env["stock.move"].browse(move_ids)

    def _no_putaway_available(self, operations):
        base_locations = self.picking_types.default_location_dest_id
        # when no putaway is found, the move line destination stays the
        # default's of the picking type
        return any(op.location_dest_id in base_locations for op in operations)

    def _find_operations_domain(self, location):
        return [
            ("location_id", "=", location.id),
            ("state", "in", ("assigned", "partially_available")),
            ("qty_done", ">", 0),
            # TODO check generated SQL
            ("picking_id.operator_id", "=", self.shopfloor_user.id),
        ]

    def _find_operations(self, location):
        """Find move lines currently being moved by the user"""
        lines = self.env["stock.pack.operation"].search(
            self._find_operations_domain(location)
        )
        return lines

    # hook used in module shopfloor_checkout_sync
    def _write_destination_on_operations(self, operations, location):
        operations.write({"location_dest_id": location.id})

    def _set_all_destination_operations_and_done(
        self, pickings, operations, dest_location
    ):
        self._write_destination_on_operations(operations, dest_location)
        stock = self._actions_for("stock")
        stock.validate_moves(operations.mapped("linked_move_operation_ids.move_id"))

    def _lock_lines(self, lines):
        """Lock move lines"""
        sql = "SELECT id FROM %s WHERE ID IN %%s FOR UPDATE" % lines._table
        self.env.cr.execute(sql, (tuple(lines.ids),), log_exceptions=False)

    def _response_for_start(self, message=None, popup=None):
        """Transition to the 'start' state"""
        return self._response(next_state="start", message=message, popup=popup)

    def _response_for_scan_destination_all(
        self, pickings, message=None, confirmation_required=False
    ):
        """Transition to the 'scan_destination_all' state

        The client screen shows a summary of all the products | lots | packages
        to move to a single destination.

        If `confirmation_required` is set,
        the client will ask to scan again the destination
        """
        data = self._data_content_all_for_location(pickings=pickings)
        data["confirmation_required"] = confirmation_required
        if confirmation_required and not message:
            message = self.msg_store.need_confirmation()
        return self._response(
            next_state="scan_destination_all", data=data, message=message
        )

    def _response_for_start_single(self, pickings, message=None, popup=None):
        """Transition to the 'start_single' state

        The client screen shows details of the operation.
        """
        location = pickings.mapped("location_id")
        next_content = self._next_content(pickings)
        if not next_content:
            # TODO test (no more lines)
            return self._response_for_start(message=message, popup=popup)
        return self._response(
            next_state="start_single",
            data=self._data_content_operation_for_location(location, next_content),
            message=message,
            popup=popup,
        )

    def _response_for_scan_destination(
        self, location, next_content, message=None, confirmation_required=False
    ):
        """Transition to the 'scan_destination' state

        The client screen shows details operations to do.
        """
        data = self._data_content_operation_for_location(location, next_content)
        data["confirmation_required"] = confirmation_required
        if confirmation_required and not message:
            message = self.msg_store.need_confirmation()
        return self._response(next_state="scan_destination", data=data, message=message)

    def _data_content_all_for_location(self, pickings):
        sorter = self._actions_for("location_content_transfer.sorter")
        sorter.feed_pickings(pickings)
        location = pickings.mapped("pack_operation_ids.location_id")
        assert len(location) == 1, "There should be only one src location at this stage"
        return {
            "location": self.data.location(location),
            "operations": self.data.operations(sorter),
        }

    def _data_content_operation_for_location(self, location, next_content):
        return {"operation": self.data.operations(next_content)[0]}

    def _next_content(self, pickings):
        sorter = self._actions_for("location_content_transfer.sorter")
        sorter.feed_pickings(pickings)
        try:
            next_content = next(sorter)
        except StopIteration:
            return None
        return next_content

    def _router_single_or_all_destination(self, pickings, message=None):
        location_dest = pickings.mapped("pack_operation_ids.location_dest_id")
        location_src = pickings.mapped("pack_operation_ids.location_id")
        if len(location_dest) == len(location_src) == 1:
            return self._response_for_scan_destination_all(pickings, message=message)
        return self._response_for_start_single(pickings, message=message)

    def _domain_recover_pickings(self):
        return [
            ("operator_id", "=", self.shopfloor_user.id),
            ("state", "=", "assigned"),
            ("picking_type_id", "in", self.picking_types.ids),
        ]

    def _search_recover_pickings(self):
        candidate_pickings = self.env["stock.picking"].search(
            self._domain_recover_pickings()
        )
        started_pickings = candidate_pickings.filtered(
            lambda picking: any(line.qty_done for line in picking.pack_operation_ids)
        )
        return started_pickings

    def _unreserve_other_operations(self, location, operations):
        """Unreserve move in location in another picking type

        Returns a tuple of (
          operations that stays in the location to process,
          moves to reserve again,
          response to return to client in case of error
        )
        """
        operations_other_picking_types = operations.filtered(
            lambda op: op.picking_id.picking_type_id not in self.picking_types
        )
        if not operations_other_picking_types:
            return (operations, self.env["stock.move"].browse(), None)
        unreserved_moves = operations.mapped("linked_move_operation_ids.move_id")
        location_operations = self.env["stock.pack.operation"].search(
            self._find_location_all_operations_domain(location)
        )
        extra_operations = location_operations - operations
        if extra_operations:
            return (
                self.env["stock.pack.operation"].browse(),
                self.env["stock.move"].browse(),
                self._response_for_start(
                    message=self.msg_store.picking_already_started_in_location(
                        extra_operations.mapped("picking_id")
                    )
                ),
            )
        unreserved_moves.do_unreserve()
        return (operations - operations_other_picking_types, unreserved_moves, None)


class ShopfloorLocationContentTransferValidator(Component):
    """Validators for the Location Content Transfer endpoints"""

    _inherit = "base.shopfloor.validator"
    _name = "shopfloor.location.content.transfer.validator"
    _usage = "location_content_transfer.validator"

    def start_or_recover(self):
        return {}

    def scan_location(self):
        return {"barcode": {"required": True, "type": "string"}}

    def set_destination_all(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
            "confirmation": {"type": "boolean", "nullable": True, "required": False},
        }

    def go_to_single(self):
        return {"location_id": {"coerce": to_int, "required": True, "type": "integer"}}

    def scan_line(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
        }

    def set_destination_line(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "lot_id": {
                "coerce": to_int,
                "required": False,
                "nullable": True,
                "type": "integer",
            },
            "quantity": {"coerce": to_float, "required": True, "type": "float"},
            "barcode": {"required": True, "type": "string"},
            "confirmation": {"type": "boolean", "nullable": True, "required": False},
        }

    def postpone_line(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
        }

    def stock_out_line(self):
        return {
            "location_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "lot_id": {
                "coerce": to_int,
                "required": False,
                "nullable": True,
                "type": "integer",
            },
        }


class ShopfloorLocationContentTransferValidatorResponse(Component):
    """Validators for the Location Content Transfer endpoints responses"""

    _inherit = "base.shopfloor.validator.response"
    _name = "shopfloor.location.content.transfer.validator.response"
    _usage = "location_content_transfer.validator.response"

    def _states(self):
        """List of possible next states

        With the schema of the data send to the client to transition
        to the next state.
        """
        return {
            "start": {},
            "scan_destination_all": self._schema_all,
            "start_single": self._schema_single,
            "scan_destination": self._schema_single,
        }

    @property
    def _schema_all(self):
        return {
            "location": self.schemas._schema_dict_of(self.schemas.location()),
            "operations": self.schemas._schema_list_of(self.schemas.operation()),
            "confirmation_required": {
                "type": "boolean",
                "nullable": True,
                "required": False,
            },
        }

    @property
    def _schema_single(self):
        return {
            "operation": self.schemas._schema_dict_of(self.schemas.operation()),
            "confirmation_required": {
                "type": "boolean",
                "nullable": True,
                "required": False,
            },
        }

    def start_or_recover(self):
        return self._response_schema(
            next_states={"start", "scan_destination_all", "start_single"}
        )

    def scan_location(self):
        return self._response_schema(
            next_states={"start", "scan_destination_all", "start_single"}
        )

    def set_destination_all(self):
        return self._response_schema(next_states={"start", "scan_destination_all"})

    def go_to_single(self):
        return self._response_schema(next_states={"start", "start_single"})

    def scan_line(self):
        return self._response_schema(
            next_states={"start", "start_single", "scan_destination"}
        )

    def set_destination_line(self):
        return self._response_schema(next_states={"start_single", "scan_destination"})

    def postpone_line(self):
        return self._response_schema(next_states={"start_single"})

    def stock_out_line(self):
        return self._response_schema(next_states={"start", "start_single"})
