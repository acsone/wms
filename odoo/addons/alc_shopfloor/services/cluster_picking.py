# -*- coding: utf-8 -*-
# Copyright 2020-2021 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields
from odoo.osv import expression
from odoo.tools import float_compare

from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from ..utils import to_float


class ClusterPicking(Component):
    """
    Methods for the Cluster Picking Process

    The goal of this scenario is to do the pickings for a Picking Batch, for
    several customers at once.
    The process assumes that picking batch records already exist.

    At first, a user gets automatically a batch to work on (assigned to them),
    or can select one from a list.

    The scenario has 2 main phases, which can be done one after the other or a
    bit of both. The first one is picking goods and put them in a roller-cage.

    First phase, picking:

    * Pick a good (move line) from a source location, scan it to confirm it's
      the expected one
    * Scan the label of a Bin (package) in a roller-cage, put the good inside
      (physically). Once the first move line of a picking has been scanned, the
      screen will show the same destination package for all the other lines of
      the picking to help the user grouping goods together, and will preventF
      lines from other pickings to be put in the same destination package.
    * If odoo thinks a source location is empty after picking the goods, a
      "zero check" is done: it asks the user to confirm if it is empty or not
    * Repeat until the end of the batch or the roller-cage is full (there is
      button to declare this)

    Second phase, unload to destination:

    * If all the goods (move lines) in the roller-cage go to the same destination,
      a screen asking a single barcode for the destination is shown
    * Otherwise, the user has to scan one destination per Bin (destination
      package of the moves).
    * If all the goods are supposed to go to the same destination but user doesn't
      want or can't, a "split" allows to reach the screen to scan one destination
      per Bin.
    * When everything has a destination set and the batch is not finished yet,
      the user goes to the first phase of pickings again for the rest.

    Inside the main workflow, some actions are accessible from the client:

    * Change a lot or pack: if the expected lot is at the very bottom of the
      location or a stock error forces a user to change lot or pack, user can
      do it during the picking.
    * Skip a line: during picking, for instance because a line is not accessible
      easily, it can be postponed, note that skipped lines have to be done, they
      are only moved to the end of the queue.
    * Declare stock out: if a good is in fact not in stock or only partially. Note
      the move lines will become unavailable or partially unavailable and will
      generate a back-order.
    * Full bin: declaring a full bin allows to move directly to the first phase
      (picking) to the second one (unload). The scenario will go
      back to the first phase if some lines remain in the queue of lines to pick.

    You will find a sequence diagram describing states and endpoints
    relationships [here](../docs/cluster_picking_diag_seq.png).
    Keep [the sequence diagram](../docs/cluster_picking_diag_seq.plantuml)
    up-to-date if you change endpoints.
    """

    _inherit = "base.shopfloor.process"
    _name = "shopfloor.cluster.picking"
    _usage = "cluster_picking"
    _description = __doc__

    def _response_for_start(self, message=None, popup=None):
        return self._response(next_state="start", message=message, popup=popup)

    def _response_for_confirm_start(self, batch):
        return self._response(
            next_state="confirm_start",
            data=self.data.picking_batch(batch, with_pickings=True),
        )

    def _response_for_manual_selection(self, batches, message=None):
        data = {
            "records": self.data.picking_batches(batches),
            "size": len(batches),
        }
        return self._response(next_state="manual_selection", data=data, message=message)

    def _response_for_start_operation(self, operation, message=None, popup=None):
        return self._response(
            next_state="start_operation",
            data=self._data_operation(operation),
            message=message,
            popup=popup,
        )

    def _response_for_scan_destination(self, operation, message=None, force_lot=None):
        data = self._data_operation(operation, force_lot=force_lot)
        last_picked_line = self._last_picked_line(operation.picking_id)
        if last_picked_line:
            # suggest pack to be used for the next line
            data["package_dest"] = self.data.package(
                last_picked_line.result_package_id.with_context(
                    picking_id=operation.picking_id.id
                ),
                picking=operation.picking_id,
            )
        return self._response(next_state="scan_destination", data=data, message=message)

    def _response_for_change_pack_lot(self, operation, message=None):
        return self._response(
            next_state="change_pack_lot",
            data=self._data_operation(operation),
            message=message,
        )

    def _response_for_zero_check(self, batch, operation):
        data = {
            "id": operation.id,
            "location_src": self.data.location(operation.location_id),
        }
        data["batch"] = self.data.picking_batch(batch)
        return self._response(next_state="zero_check", data=data)

    def _response_for_unload_all(self, batch, message=None):
        return self._response(
            next_state="unload_all",
            data=self._data_for_unload_all(batch),
            message=message,
        )

    def _response_for_confirm_unload_all(self, batch, message=None):
        return self._response(
            next_state="confirm_unload_all",
            data=self._data_for_unload_all(batch),
            message=message,
        )

    def _response_for_unload_single(self, batch, package, message=None, popup=None):
        return self._response(
            next_state="unload_single",
            data=self._data_for_unload_single(batch, package),
            message=message,
            popup=popup,
        )

    def _response_for_unload_set_destination(self, batch, package, message=None):
        return self._response(
            next_state="unload_set_destination",
            data=self._data_for_unload_single(batch, package),
            message=message,
        )

    def _response_for_confirm_unload_set_destination(self, batch, package):
        return self._response(
            next_state="confirm_unload_set_destination",
            data=self._data_for_unload_single(batch, package),
        )

    def find_batch(self):
        """Find a picking batch to work on and start it

        Usually the starting point of the scenario.

        Business rules to find a batch, try in order:

        a. Find a batch in progress assigned to the current user
        b. Find a draft batch assigned to the current user:
          1. set it to 'in progress'
        c. Find an unassigned draft batch:
          1. assign batch to the current user
          2. set it to 'in progress'

        Transitions:
        * confirm_start: when it could find a batch
        * start: when no batch is available
        """
        batches = self._batch_picking_search()
        selected = self._select_a_picking_batch(batches)
        if selected:
            return self._response_for_confirm_start(selected)
        return self._response_for_start(
            message={
                "message_type": "info",
                "body": _("No more work to do, please create a new batch transfer"),
            },
        )

    def list_batch(self):
        """List picking batch on which user can work

        Returns a list of all the available records for the current picking
        type.

        Transitions:
        * manual_selection: to the selection screen
        """
        batches = self._batch_picking_search()
        return self._response_for_manual_selection(batches)

    def _batch_picking_base_search_domain(self):
        return [
            "|",
            "&",
            ("user_id", "=", False),
            ("state", "=", "draft"),
            "&",
            ("user_id", "=", self.shopfloor_user.id),
            ("state", "in", ("draft", "in_progress")),
        ]

    def _batch_picking_search(self, name_fragment=None, batch_ids=None):
        domain = self._batch_picking_base_search_domain()
        if name_fragment:
            domain = expression.AND([domain, [("name", "ilike", name_fragment)]])
        if batch_ids:
            domain = expression.AND([domain, [("id", "in", batch_ids)]])
        records = self.env["stock.picking.wave"].search(domain, order="id asc")
        records = records.filtered(self._batch_filter)
        return records

    def _batch_filter(self, batch):
        if not batch.picking_ids:
            return False
        return batch.picking_ids.filtered(self._batch_picking_filter)

    def _batch_picking_filter(self, picking):
        # Picking type guard
        if picking.picking_type_id not in self.picking_types:
            return False
        # Include done/cancel because we want to be able to work on the
        # batch even if some pickings are done/canceled. They'll should be
        # ignored later.
        # When the batch is already in progress, we do not care
        # about state of the pickings, because we want to be able
        # to recover it in any case, even if, for instance, a stock
        # error changed a picking to unavailable after the user
        # started to work on the batch.
        return picking.batch_id.state == "in_progress" or picking.state in (
            "assigned",
            "done",
            "cancel",
        )

    def _select_a_picking_batch(self, batches):
        # look for in progress + assigned to self first
        candidates = batches.filtered(
            lambda batch: batch.state == "in_progress"
            and batch.user_id == self.shopfloor_user
        )
        if candidates:
            return candidates[0]
        # then look for draft assigned to self
        candidates = batches.filtered(
            lambda batch: batch.user_id == self.shopfloor_user
        )
        if candidates:
            batch = candidates[0]
            batch.write({"state": "in_progress"})
            return batch
        # finally take any batch that search could return
        if batches:
            batch = batches[0]
            batch.write({"user_id": self.shopfloor_user.id, "state": "in_progress"})
            return batch
        return self.env["stock.picking.wave"]

    def select(self, picking_batch_id):
        """Manually select a picking batch

        The client application can use the service /picking_batch/search
        to get the list of candidate batches. Then, it starts to work on
        the selected batch by calling this.

        Note: it should be able to work only on batches which are in draft or
        (in progress and assigned to the current user), the search method that
        lists batches filter them, but it has to be checked again here in case
        of race condition.

        Transitions:
        * manual_selection: a selected batch cannot be used (assigned to someone else
          concurrently for instance)
        * confirm_start: after the batch has been assigned to the user
        """
        batches = self._batch_picking_search(batch_ids=[picking_batch_id])
        selected = self._select_a_picking_batch(batches)
        if selected:
            return self._response_for_confirm_start(selected)
        return self._response(
            base_response=self.list_batch(),
            message={
                "message_type": "warning",
                "body": _("This batch cannot be selected."),
            },
        )

    def confirm_start(self, picking_batch_id):
        """User confirms they start a batch

        Should have no effect in odoo besides logging and routing the user to
        the next action. The next action is "start_operation" with data about the
        line to pick.

        Transitions:
        * start_operation: when the batch has at least one line without destination
          package
        * start: if the condition above is wrong (rare case of race condition...)
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        return self._pick_next_operation(batch)

    def _pick_next_operation(self, batch, message=None, force_operation=None):
        if force_operation:
            next_operation = force_operation
        else:
            next_operation = self._next_operation_for_pick(batch)
        if not next_operation:
            return self.prepare_unload(batch.id)
        return self._response_for_start_operation(next_operation, message=message)

    @staticmethod
    def _sort_key_operations(operation):
        return (
            operation.shopfloor_priority or 10,
            operation.location_id.shopfloor_picking_sequence or "",
            operation.location_id.name,
            -int(min(operation.move_ids.mapped("priority") or "0")),
            min(operation.move_ids.mapped("date_expected")),
            -int(min(operation.move_ids.mapped("sequence") or "0")),
            min(operation.move_ids.ids),
            # operation.id,
        )

    def _operations_for_picking_batch(self, picking_batch, filter_func=lambda x: x):
        lines = picking_batch.mapped("picking_ids.pack_operation_ids").filtered(
            filter_func
        )
        # TODO test line sorting and all these methods to retrieve lines

        # Sort line by source location,
        # so that the picker start w/ products in the same location.
        # Postponed lines must come always
        # after ALL the other lines in the batch are processed.
        return lines.sorted(key=self._sort_key_operations)

    def _operations_to_do(self, picking_batch):
        return self._operations_for_picking_batch(
            picking_batch,
            filter_func=lambda l: (
                l.state in ("assigned", "partially_available")
                # On 'StockPicking.action_assign()', result_package_id is set to
                # the same package as 'package_id'. Here, we need to exclude lines
                # that were already put into a bin, i.e. the destination package
                # is different.
                and (not l.result_package_id or l.result_package_id == l.package_id)
            ),
        )

    def _last_picked_line(self, picking):
        """Get the last line picked and put in a pack for this picking"""
        return fields.first(
            picking.pack_operation_ids.filtered(
                lambda l: l.qty_done > 0
                and l.result_package_id
                # if we are moving the entire package, we shouldn't
                # add stuff inside it, it's not a new package
                and l.package_id != l.result_package_id
            ).sorted(key="write_date", reverse=True)
        )

    def _next_operation_for_pick(self, picking_batch):
        remaining_operations = self._operations_to_do(picking_batch)
        return fields.first(remaining_operations)

    def _response_batch_does_not_exist(self):
        return self._response_for_start(message=self.msg_store.record_not_found())

    def _data_operation(self, operation, force_lot=None, **kw):
        picking = operation.picking_id
        batch = picking.batch_id
        product = operation.product_id
        operations = self.data.operations(operation)
        data = None
        if force_lot:
            for op in operations:
                if op.get("lot", {}).get("id") == force_lot.id:
                    data = op
                    break
            if not data:
                raise SystemError("Force lot not found into operation")
        else:
            data = operations[0]
        # additional values
        # Ensure destination pack is never proposed on the frontend.
        # This should happen only as proposal on `scan_destination`
        # where we set the last used package.
        data["package_dest"] = None
        data["batch"] = self.data.picking_batch(batch)
        data["picking"] = self.data.picking(picking)
        data["postponed"] = operation.shopfloor_postponed
        data["product"]["qty_available"] = product.with_context(
            location=operation.location_id.id
        ).qty_available
        data.update(kw)
        return data

    def _cancel_batch(self, picking_batch_id):
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if batch.exists():
            batch.write({"state": "draft", "user_id": False})
        return batch

    def unassign(self, picking_batch_id):
        """Unassign and reset to draft a started picking batch

        Transitions:
        * "start" to work on a new batch
        """
        self._cancel_batch(picking_batch_id)
        return self._response_for_start()

    def scan_line(self, picking_batch_id, operation_id, barcode, lot_id=False):
        """Scan a location, a pack, a product or a lots

        There is no side-effect, it is only to check that the operator takes
        the expected pack or product.

        User can scan a location if there is only pack inside. Otherwise, they
        have to precise what they want by scanning one of:

        * pack
        * product
        * lot

        The result must be unambigous. For instance if we scan a product but the
        product is tracked by lot, scanning the lot has to be required.

        Transitions:
        * start_operation: with an appropriate message when user has
          to scan for the same line again
        * start_operation: with the next line if the line was added to a
          pack meanwhile (race condition).
        * scan_destination: if the barcode matches.
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            return self._pick_next_operation(
                batch, message=self.msg_store.operation_not_found()
            )

        search = self._actions_for("search")

        picking = operation.picking_id

        package = search.package_from_scan(barcode)
        if package and operation.package_id == package:
            return self._scan_line_by_package(picking, operation, package)

        # use the common search method so we search by packaging too
        product = search.product_from_scan(barcode)
        if (
            product
            and operation.product_id == product
            or product
            in operation.package_id._get_contained_quants().mapped("product_id")
        ):
            return self._scan_line_by_product(picking, operation, product)

        lot = search.lot_from_scan(barcode, product=operation.product_id)

        if lot and (
            (lot in operation.mapped("pack_lot_ids.lot_id"))
            or (lot in operation.package_id._get_contained_quants().mapped("lot_id"))
            or lot_id
        ):
            return self._scan_line_by_lot(picking, operation, lot, lot_id)

        location = search.location_from_scan(barcode)
        if location and operation.location_id == location:
            return self._scan_line_by_location(picking, operation, location)

        # Nothing matches what is expected from the operation.
        for rec in (package, product, lot, location):
            if rec:
                return self._response_for_start_operation(
                    operation, message=self.msg_store.wrong_record(rec)
                )

        return self._response_for_start_operation(
            operation, message=self.msg_store.barcode_not_found()
        )

    def _scan_line_by_package(self, picking, operation, package):
        """Package scanned, just work with it."""
        return self._response_for_scan_destination(operation)

    def _scan_line_by_product(self, picking, operation, product):
        """Product scanned, check if we can work with it.

        If scanned product is part of several packages in the same location,
        we can't be sure it's the correct one, in such case, ask to scan a package
        """
        if operation.product_id.tracking in ("lot", "serial"):
            return self._response_for_start_operation(
                operation, message=self.msg_store.scan_lot_on_product_tracked_by_lot()
            )
        other_product_operation_ids = []
        for op in picking.pack_operation_ids.filtered(
            lambda o, ori=operation: ori.location_id == o.location_id
        ):
            if op.product_id == product:
                other_product_operation_ids.append(op.id)
                continue
            if op.package_id and product in op.package_id._get_contained_quants().mapped(
                "product_id"
            ):
                other_product_operation_ids.append(op.id)
        # if we have more than one package,
        # but also if we have one product as a package and the same product as
        # a unit in another line. In both cases, we want the user to scan the
        # package.
        if other_product_operation_ids and len(other_product_operation_ids) > 1:
            return self._response_for_start_operation(
                operation,
                message=self.msg_store.product_multiple_packages_scan_package(),
            )
        return self._response_for_scan_destination(operation)

    def _scan_line_by_lot(self, picking, operation, lot, lot_id):
        """Lot scanned, check if we can work with it.

        If we scanned a lot and it's part of several packages, we can't be
        sure the user scanned the correct one, in such case, ask to scan a package
        """
        other_lot_operation_ids = []
        #  we want to see if we have more than one
        # package, but also if we have one lot as a package and the same lot as
        # a unit in another line. In both cases, we want the user to scan the
        # package.
        for op in picking.pack_operation_ids:
            if lot in op.mapped("pack_lot_ids.lot_id"):
                other_lot_operation_ids.append(op.id)
                continue
            if op.package_id and lot in op.package_id._get_contained_quants().mapped(
                "lot_id"
            ):
                other_lot_operation_ids.append(op.id)
        if other_lot_operation_ids and len(other_lot_operation_ids) > 1:
            # We already processed some quantities for this lot on same location,
            # we filter the operation with no quantity done. If there is more than one,
            # then you need to scan location to reconcile quanitities
            other_lot_operation = self.env["stock.pack.operation"].browse(
                other_lot_operation_ids
            )
            operations = other_lot_operation.filtered(lambda op: op.qty_done <= 0)
            if len(operations) > 1:
                return self._response_for_start_operation(
                    operation,
                    message=self.msg_store.lot_multiple_packages_scan_location(),
                )
            operation = operations
        if lot_id and lot.id != lot_id:
            return self._response_for_start_operation(
                operation, message=self.msg_store.wrong_lot_scanned(),
            )
        return self._response_for_scan_destination(operation)

    def _scan_line_by_location(self, picking, operation, location):
        """Location scanned, check if we can work on goods contained into it.

        When a user scan a location, we accept only when we knows that
        they scanned the good thing, so if in the location we have
        several lots (on a package or a product), several packages,
        several products or a mix of several products and packages, we
        ask to scan a more precise barcode.
        """
        location = operation.location_id
        ml_search = self.search_pack_operation
        pending_operations = ml_search.search_pack_operations_by_location(location)

        lots = (
            pending_operations.mapped("pack_lot_ids")
            .filtered(
                lambda l: float_compare(
                    l.qty,
                    l.qty_todo,
                    precision_rounding=l.operation_id.product_uom_id.rounding,
                )
                < 0
            )
            .mapped("lot_id")
        )

        if len(lots) > 1:
            return self._response_for_start_operation(
                operation,
                message=self.msg_store.several_lots_in_location(operation.location_id),
            )

        packages = pending_operations.mapped("package_id")
        products = pending_operations.mapped("product_id")

        if len(packages) > 1 or len(products) > 1:
            if operation.package_id:
                return self._response_for_start_operation(
                    operation,
                    message=self.msg_store.several_packs_in_location(
                        operation.location_id
                    ),
                )
            return self._response_for_start_operation(
                operation,
                message=self.msg_store.several_products_in_location(
                    operation.location_id
                ),
            )

        return self._response_for_scan_destination(operation)

    def scan_destination_pack(
        self, picking_batch_id, operation_id, barcode, quantity, lot_id=None
    ):
        """Scan the destination package (bin) for a move line

        If the quantity picked (passed to the endpoint) is < expected quantity,
        it splits the move line.
        It changes the destination package of the move line and set the "qty done".
        It prevents to put a move line of a picking in a destination package
        used for another picking.

        Transitions:
        * zero_check: if the quantity of product moved is 0 in the
        source location after the move (beware: at this point the product we put in
        a bin is still considered to be in the source location, so we have to compute
        the source location's quantity - qty_done).
        * unload_all: when all lines have a destination package and they all
        have the same destination.
        * unload_single: when all lines have a destination package and they all
        have the same destination.
        * start_operation: to pick the next line if any.
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            return self._pick_next_operation(
                batch, message=self.msg_store.operation_not_found()
            )

        if lot_id and lot_id not in operation.pack_lot_ids.mapped("lot_id").ids:
            message = self.msg_store.lot_not_found_on_operation(lot_id, operation.id)
            return self._response_for_scan_destination(operation, message=message)

        if operation.pack_lot_ids and not lot_id:
            return self._response_for_scan_destination(
                operation, message=self.msg_store.scan_lot_on_product_tracked_by_lot(),
            )

        search = self._actions_for("search")
        bin_package = search.package_from_scan(barcode)

        if not bin_package:
            return self._response_for_scan_destination(
                operation, message=self.msg_store.bin_not_found_for_barcode(barcode)
            )

        if quantity <= 0:
            return self._response_for_scan_destination(
                operation, message=self.msg_store.qty_must_be_greater_than_zero()
            )

        # the scanned package can contain only move lines of the same picking
        if bin_package.quant_ids or self._check_picking_condition(
            bin_package, operation
        ):
            return self._response_for_scan_destination(
                operation,
                message={
                    "message_type": "error",
                    "body": _(
                        "The destination bin {} is not empty, please take another."
                    ).format(bin_package.name),
                },
            )

        new_line, qty_check = operation._split_qty_to_be_done(quantity, lot_id=lot_id)
        if qty_check == "greater":
            return self._response_for_scan_destination(
                operation,
                message=self.msg_store.unable_to_pick_more(operation.product_qty),
            )
        operation.write({"qty_done": quantity, "result_package_id": bin_package.id})

        zero_check = operation.picking_id.picking_type_id.shopfloor_zero_check
        if zero_check and operation.location_id.planned_qty_in_location_is_empty():
            return self._response_for_zero_check(batch, operation)

        return self._pick_next_operation(
            batch,
            message=self.msg_store.x_units_put_in_package(
                operation.qty_done, operation.product_id, operation.result_package_id
            ),
            # if we split the move line, we want to process the one generated by the
            # split right now
            force_operation=new_line,
        )

    def _check_picking_condition(self, bin_package, operation):
        if any(
            ml.picking_id != operation.picking_id
            for ml in bin_package.planned_pack_operation_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )
        ):
            return True
        return False

    def _are_all_dest_location_same(self, batch):
        lines_to_unload = self._lines_to_unload(batch)
        return len(lines_to_unload.mapped("location_dest_id")) == 1

    def prepare_unload(self, picking_batch_id):
        """Initiate the unloading phase of the scenario

        It goes to different screens depending if all the move lines have
        the same destination or not.

        Transitions:
        * unload_all: when all lines go to the same destination
        * unload_single: when lines have different destinations
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        if self._are_all_dest_location_same(batch):
            return self._response_for_unload_all(batch)
        # the lines have different destinations
        return self._unload_next_package(batch)

    def _data_for_unload_all(self, batch):
        lines = self._lines_to_unload(batch)
        # all the lines destinations are the same here, it looks
        # only for the first one
        first_line = fields.first(lines)
        data = self.data.picking_batch(batch)
        data.update({"location_dest": self.data.location(first_line.location_dest_id)})
        return data

    def _data_for_unload_single(self, batch, package):
        line = fields.first(
            package.planned_pack_operation_ids.filtered(self._filter_for_unload)
        )
        data = self.data.picking_batch(batch)
        data.update(
            {
                "package": self.data.package(package),
                "location_dest": self.data.location(line.location_dest_id),
            }
        )
        return data

    def _filter_for_unload(self, line):
        return (
            line.state in ("assigned", "partially_available")
            and line.qty_done > 0
            and line.result_package_id
            and not line.shopfloor_unloaded
        )

    def _lines_to_unload(self, batch):
        return self._operations_for_picking_batch(
            batch, filter_func=self._filter_for_unload
        )

    def _bin_packages_to_unload(self, batch):
        lines = self._lines_to_unload(batch)
        packages = lines.mapped("result_package_id").sorted()
        return packages

    def _next_bin_package_for_unload_single(self, batch):
        packages = self._bin_packages_to_unload(batch)
        return fields.first(packages)

    def is_zero(self, picking_batch_id, operation_id, zero):
        """Confirm or not if the source location of a move has zero qty

        If the user confirms there is zero quantity, it means the stock was
        correct and there is nothing to do. If the user says "no", a draft
        empty inventory is created for the product (with lot if tracked).

        Transitions:
        * start_operation: if the batch has lines without destination package (bin)
        * unload_all: if all lines have a destination package and same
          destination
        * unload_single: if all lines have a destination package and different
          destination
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            return self._pick_next_operation(
                batch, message=self.msg_store.operation_not_found()
            )

        if not zero:
            inventory = self._actions_for("inventory")
            inventory.create_draft_check_empty(
                operation.location_id,
                operation.product_id,
                ref=operation.picking_id.name,
            )

        return self._pick_next_operation(
            batch,
            message=self.msg_store.x_units_put_in_package(
                operation.qty_done, operation.product_id, operation.result_package_id
            ),
        )

    def skip_operation(self, picking_batch_id, operation_id):
        """Skip a line. The line will be processed at the end.

        It adds a flag on the move line, when the next line to pick
        is searched, lines with such flag at moved to the end.

        A skipped line *must* be picked.

        Transitions:
        * start_operation: with data for the next line (or itself if it's the last one,
        in such case, a helpful message is returned)
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            return self._pick_next_operation(
                batch, message=self.msg_store.operation_not_found()
            )
        # flag as postponed
        operation.shopfloor_postpone(self._operations_to_do(batch))
        return self._pick_after_skip_operation(operation)

    def _pick_after_skip_operation(self, operation):
        batch = operation.picking_id.batch_id
        return self._pick_next_operation(batch)

    def stock_issue(self, picking_batch_id, operation_id, lot_id=False):
        """Declare a stock issue for a line

        After errors in the stock, the user cannot take all the products
        because there is physically not enough goods. The move line is deleted
        (unreserve), and an inventory is created to reduce the quantity in the
        source location to prevent future errors until a correction. Beware:
        the quantity already reserved by other lines should remain reserved so
        the inventory's quantity must be set to the quantity of lines reserved
        by other move lines (but not the current one).

        The other lines not yet picked in the batch for the same product, lot,
        package are unreserved as well (moves lines deleted, which unreserve
        their quantity on the move).

        A second inventory is created in draft to have someone do an inventory
        check.

        Transitions:
        * start_operation: when the batch still contains lines without destination
          package
        * unload_all: if all lines have a destination package and same
          destination
        * unload_single: if all lines have a destination package and different
          destination
        * start: all lines are done/confirmed (because all lines were unloaded
          and the last line has a stock issue). In this case, this method *has*
          to handle the closing of the batch to create backorders (_unload_end)
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            return self._pick_next_operation(
                batch, message=self.msg_store.operation_not_found()
            )
        if lot_id and lot_id not in operation.pack_lot_ids.mapped("lot_id").ids:
            return self._response_for_scan_destination(
                operation, message=self.msg_store.record_not_found(),
            )

        if operation.pack_lot_ids and not lot_id:
            return self._response_for_scan_destination(
                operation, message=self.msg_store.scan_lot_on_product_tracked_by_lot(),
            )

        lot = self.env["stock.production.lot"].browse(lot_id)
        domain = self._domain_stock_issue_similar_operations(
            operation=operation, lot=lot
        )
        operations_to_block = operation | self.env["stock.pack.operation"].search(
            domain
        )
        # split operations done into others move
        for move in operations_to_block.mapped("move_ids"):
            done_operations = move.pack_operation_ids.filtered("is_done")
            if done_operations:
                move.split_other_pack_operations(done_operations, intersection=True)
                operations_to_block = operations_to_block - done_operations
        operations_to_block._skip_operation(lot=lot)

        return self._pick_next_operation(batch)

    def _domain_stock_issue_similar_operations(self, operation, lot):
        # Since we have not enough stock, delete the move lines, which will
        # in turn unreserve the moves. The moves lines we delete are those
        # in the same batch (we don't want to interfere with other operators
        # work, they'll have to declare a stock issue), and not yet started.
        # The goal is to prevent the same operator to declare twice the same
        # stock issue for the same product/lot/package.
        batch = operation.picking_id.batch_id
        package = operation.package_id
        location = operation.location_id
        product = operation.product_id
        domain = [
            ("location_id", "=", location.id),
            ("product_id", "=", product.id),
            ("package_id", "=", package.id),
            ("state", "not in", ("cancel", "done")),
            ("qty_done", "=", 0),
            ("picking_id.batch_id", "=", batch.id),
        ]
        if lot:
            domain.append(("pack_lot_ids.lot_id", "=", lot.id))
        return domain

    def change_pack_lot(self, picking_batch_id, operation_id, barcode, lot_id=None):
        """Change the expected pack or the lot for a line

        If the expected lot is at the very bottom of the location or a stock
        error forces a user to change lot or pack, user can change the pack or
        lot of the current line.

        The change occurs when the pack/product/lot is normally scanned and
        goes directly to the scan of the destination package (bin) since we do
        not need to check it.

        If the pack or lot was not supposed to be in the source location,
        a draft inventory is created to have this checked.

        Transitions:
        * scan_destination: the pack or the lot could be changed
        * change_pack_lot: any error occurred during the change
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            return self._pick_next_operation(
                batch, message=self.msg_store.operation_not_found()
            )
        search = self._actions_for("search")
        response_ok_func = self._response_for_scan_destination
        response_error_func = self._response_for_change_pack_lot
        change_package_lot = self._actions_for("change.package.lot")
        lot = search.lot_from_scan(barcode, product=operation.product_id)
        if lot and lot_id:
            old_lot = self.env["stock.production.lot"].browse(lot_id)
            check_lot = change_package_lot.check_new_lot(
                operation=operation,
                new_lot=lot,
                old_lot=old_lot,
                response_error_func=response_error_func,
            )
            if check_lot:
                return check_lot
            response = change_package_lot.change_lot(
                operation,
                previous_lot=old_lot,
                new_lot=lot,
                response_ok_func=response_ok_func,
                response_error_func=response_error_func,
            )
            if response:
                return response

        package = search.package_from_scan(barcode)
        if package:
            return change_package_lot.change_package(
                operation, package, response_ok_func, response_error_func
            )

        return self._response_for_change_pack_lot(
            operation, message=self.msg_store.no_package_or_lot_for_barcode(barcode),
        )

    def set_destination_all(self, picking_batch_id, barcode, confirmation=False):
        """Set the destination for all the lines of the batch with a dest. package

        This method must be used only if all the move lines which have a destination
        package and qty done have the same destination location.

        A scanned location outside of the source location of the operation type is
        invalid.

        Transitions:
        * start_operation: the batch still have move lines without destination package
        * unload_all: invalid destination, have to scan a good one
        * confirm_unload_all: the scanned location is not the expected one (but
          still a valid one)
        * start: batch is totally done. In this case, this method *has*
          to handle the closing of the batch to create backorders.
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()

        # In case /set_destination_all was called and the destinations were
        # in fact no the same... restart the unloading step over
        if not self._are_all_dest_location_same(batch):
            return self.prepare_unload(batch.id)

        lines = self._lines_to_unload(batch)
        if not lines:
            return self._unload_end(batch)

        first_line = fields.first(lines)
        scanned_location = self._actions_for("search").location_from_scan(barcode)
        if not scanned_location:
            return self._response_for_unload_all(
                batch, message=self.msg_store.no_location_found()
            )
        if not self.is_dest_location_valid(lines.mapped("move_ids"), scanned_location):
            return self._response_for_unload_all(
                batch, message=self.msg_store.dest_location_not_allowed()
            )

        if not confirmation and self.is_dest_location_to_confirm(
            first_line.location_dest_id, scanned_location
        ):
            return self._response_for_confirm_unload_all(batch)

        self._unload_write_destination_on_lines(lines, scanned_location)
        completion_info = self._actions_for("completion.info")
        completion_info_popup = completion_info.popup(lines)
        return self._unload_end(batch, completion_info_popup=completion_info_popup)

    def _unload_write_destination_on_lines(self, lines, location):
        lines.write({"shopfloor_unloaded": True, "location_dest_id": location.id})
        for line in lines:
            # We set the picking to done only when the last line is
            # unloaded to avoid backorders.
            picking = line.picking_id
            if picking.state == "done":
                continue
            operations = picking.mapped("pack_operation_ids")
            if all(p.shopfloor_unloaded for p in operations):
                self._do_transfer(pickings=picking)

    def _do_transfer(self, pickings):
        for picking in pickings:
            if picking.pack_operation_ids:
                picking.do_transfer()
        pickings_not_done = pickings.filtered(lambda p: p.state != "done")
        pickings_not_done.write({"batch_id": False})

    def _unload_end(self, batch, completion_info_popup=None):
        """Try to close the batch if all transfers are done.

        Returns to `start_operation` transition if some lines could still be processed,
        otherwise try to validate all the transfers of the batch.
        """
        if all(picking.state == "done" for picking in batch.picking_ids):
            # do not use the 'done()' method because it does many things we
            # don't care about
            batch.state = "done"
            return self._response_for_start(
                message=self.msg_store.batch_transfer_complete(),
                popup=completion_info_popup,
            )

        next_line = self._next_operation_for_pick(batch)
        if next_line:
            return self._response_for_start_operation(
                next_line,
                message=self.msg_store.batch_transfer_line_done(),
                popup=completion_info_popup,
            )
        # because a move was unassigned, we want to validate the batch to
        # produce backorders)
        self._do_transfer(pickings=batch.mapped("picking_ids"))
        batch.state = "done"
        # Unassign not validated pickings from the batch, they will be
        # processed in another batch automatically later on

        # CODE MOVED to async exec of picking validation....
        # pickings_not_done = batch.mapped("picking_ids").filtered(
        #    lambda p: p.state != "done"
        # )
        # pickings_not_done.write({"batch_id": False})
        # END CODE MOVED

        return self._response_for_start(
            message=self.msg_store.batch_transfer_complete(),
            popup=completion_info_popup,
        )

    def unload_split(self, picking_batch_id):
        """Indicates that now the batch must be treated line per line

        Even if the move lines to unload all have the same destination.

        Note: if we go back to the first phase of picking and start a new
        phase of unloading, the flag is reevaluated to the initial condition.

        Transitions:
        * unload_single: always goes here since we now want to unload line per line
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()

        return self._unload_next_package(batch)

    def unload_scan_pack(self, picking_batch_id, package_id, barcode):
        """Check that the operator scans the correct package (bin) on unload

        If the scanned barcode is not the one of the Bin (package), ask to scan
        again.

        Transitions:
        * unload_single: if the barcode does not match
        * unload_set_destination: barcode is correct
        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        package = self.env["stock.quant.package"].browse(package_id)
        if not package.exists():
            return self._unload_next_package(batch)
        if package.name != barcode:
            return self._response_for_unload_single(
                batch,
                package,
                message={"message_type": "error", "body": _("Wrong bin")},
            )
        return self._response_for_unload_set_destination(batch, package)

    def unload_scan_destination(
        self, picking_batch_id, package_id, barcode, confirmation=False
    ):
        """Scan the final destination for all the move lines moved with the Bin

        It updates all the assigned move lines with the package to the
        destination.

        Transitions:
        * unload_single: invalid scanned location or error
        * unload_single: line is processed and the next bin can be unloaded
        * confirm_unload_set_destination: the destination is valid but not the
          expected, ask a confirmation. This state has to call again the
          endpoint with confirmation=True
        * start_operation: if the batch still has lines to pick
        * start: if the batch is done. In this case, this method *has*
          to handle the closing of the batch to create backorders.

        """
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()

        package = self.env["stock.quant.package"].browse(package_id)
        if not package.exists():
            return self._unload_next_package(batch)

        # we work only on the lines of the scanned package
        lines = self._lines_to_unload(batch).filtered(
            lambda l: l.result_package_id == package
        )
        if not lines:
            return self._unload_end(batch)

        return self._unload_scan_destination_lines(
            batch, package, lines, barcode, confirmation=confirmation
        )

    def _lock_lines(self, lines):
        """Lock move lines"""
        sql = "SELECT id FROM %s WHERE ID IN %%s FOR UPDATE" % lines._table
        self.env.cr.execute(sql, (tuple(lines.ids),), log_exceptions=False)

    def _unload_scan_destination_lines(
        self, batch, package, lines, barcode, confirmation=False
    ):
        # Lock move lines that will be updated
        self._lock_lines(lines)
        first_line = fields.first(lines)
        scanned_location = self._actions_for("search").location_from_scan(barcode)
        if not scanned_location:
            return self._response_for_unload_set_destination(
                batch, package, message=self.msg_store.no_location_found()
            )
        if not self.is_dest_location_valid(lines.mapped("move_ids"), scanned_location):
            return self._response_for_unload_set_destination(
                batch, package, message=self.msg_store.dest_location_not_allowed()
            )
        if not confirmation and self.is_dest_location_to_confirm(
            first_line.location_dest_id, scanned_location
        ):
            return self._response_for_confirm_unload_set_destination(batch, package)

        self._unload_write_destination_on_lines(lines, scanned_location)

        completion_info = self._actions_for("completion.info")
        completion_info_popup = completion_info.popup(lines)

        return self._unload_next_package(
            batch, completion_info_popup=completion_info_popup
        )

    def _unload_next_package(self, batch, completion_info_popup=None):
        next_package = self._next_bin_package_for_unload_single(batch)
        if next_package:
            return self._response_for_unload_single(
                batch, next_package, popup=completion_info_popup
            )
        return self._unload_end(batch, completion_info_popup=completion_info_popup)


class ShopfloorClusterPickingValidator(Component):
    """Validators for the Cluster Picking endpoints"""

    _inherit = "base.shopfloor.validator"
    _name = "shopfloor.cluster_picking.validator"
    _usage = "cluster_picking.validator"

    def find_batch(self):
        return {}

    def list_batch(self):
        return {}

    def select(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"}
        }

    def confirm_start(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"}
        }

    def unassign(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"}
        }

    def scan_line(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
            "lot_id": {"coerce": to_int, "required": False, "type": "integer"},
        }

    def scan_destination_pack(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
            "quantity": {"coerce": to_float, "required": True, "type": "float"},
            "lot_id": {"coerce": to_int, "required": False, "type": "integer"},
        }

    def prepare_unload(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"}
        }

    def is_zero(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "zero": {"coerce": to_bool, "required": True, "type": "boolean"},
        }

    def skip_operation(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
        }

    def stock_issue(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "lot_id": {"coerce": to_int, "required": False, "type": "integer"},
        }

    def change_pack_lot(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
            "lot_id": {"coerce": to_int, "required": False, "type": "integer"},
        }

    def set_destination_all(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
            "confirmation": {"type": "boolean", "nullable": True, "required": False},
        }

    def unload_split(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"}
        }

    def unload_scan_pack(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "package_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
        }

    def unload_scan_destination(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "package_id": {"coerce": to_int, "required": True, "type": "integer"},
            "barcode": {"required": True, "type": "string"},
            "confirmation": {"type": "boolean", "nullable": True, "required": False},
        }


class ShopfloorClusterPickingValidatorResponse(Component):
    """Validators for the Cluster Picking endpoints responses"""

    _inherit = "base.shopfloor.validator.response"
    _name = "shopfloor.cluster_picking.validator.response"
    _usage = "cluster_picking.validator.response"

    def _states(self):
        """List of possible next states

        With the schema of the data send to the client to transition
        to the next state.
        """
        return {
            "confirm_start": self._schema_for_batch_details,
            "start_operation": self._schema_for_single_line_details,
            "start": {},
            "manual_selection": self._schema_for_batch_selection,
            "scan_destination": self._schema_for_single_line_details,
            "zero_check": self._schema_for_zero_check,
            "unload_all": self._schema_for_unload_all,
            "confirm_unload_all": self._schema_for_unload_all,
            "unload_single": self._schema_for_unload_single,
            "unload_set_destination": self._schema_for_unload_single,
            "confirm_unload_set_destination": self._schema_for_unload_single,
            "change_pack_lot": self._schema_for_single_line_details,
        }

    def find_batch(self):
        return self._response_schema(next_states={"confirm_start"})

    def list_batch(self):
        return self._response_schema(next_states={"manual_selection"})

    def select(self):
        return self._response_schema(next_states={"manual_selection", "confirm_start"})

    def confirm_start(self):
        return self._response_schema(
            next_states={
                "start_operation",
                # we reopen a batch already started where all the lines were
                # already picked and have to be unloaded to the same
                # destination
                "unload_all",
                # we reopen a batch already started where all the lines were
                # already picked and have to be unloaded to the different
                # destinations
                "unload_single",
            }
        )

    def unassign(self):
        return self._response_schema(next_states={"start"})

    def scan_line(self):
        return self._response_schema(
            next_states={"start_operation", "scan_destination"}
        )

    def scan_destination_pack(self):
        return self._response_schema(
            next_states={
                # error during scan of pack (wrong barcode, ...)
                "scan_destination",
                # when we still have lines to process
                "start_operation",
                # when the source location is empty
                "zero_check",
                # when all lines have been processed and have same
                # destination
                "unload_all",
                # when all lines have been processed and have different
                # destinations
                "unload_single",
            }
        )

    def prepare_unload(self):
        return self._response_schema(
            next_states={
                # when all lines have been processed and have same
                # destination
                "unload_all",
                # when all lines have been processed and have different
                # destinations
                "unload_single",
            }
        )

    def is_zero(self):
        return self._response_schema(
            next_states={
                # when we still have lines to process
                "start_operation",
                # when all lines have been processed and have same
                # destination
                "unload_all",
                # when all lines have been processed and have different
                # destinations
                "unload_single",
            }
        )

    def skip_operation(self):
        return self._response_schema(next_states={"start_operation"})

    def stock_issue(self):
        return self._response_schema(
            next_states={
                # when we still have lines to process
                "start_operation",
                # when all lines have been processed and have same
                # destination
                "unload_all",
                # when all lines have been processed and have different
                # destinations
                "unload_single",
            }
        )

    def change_pack_lot(self):
        return self._response_schema(
            next_states={"change_pack_lot", "scan_destination"}
        )

    def set_destination_all(self):
        return self._response_schema(
            next_states={
                # if the batch still contain lines
                "start_operation",
                # invalid destination, have to scan a valid one
                "unload_all",
                # this endpoint was called but after checking, lines
                # have different destination locations
                "unload_single",
                # different destination to confirm
                "confirm_unload_all",
                # batch finished
                "start",
            }
        )

    def unload_split(self):
        return self._response_schema(next_states={"unload_single"})

    def unload_scan_pack(self):
        return self._response_schema(
            next_states={
                # go back to the same state if barcode issue
                "unload_single",
                # if the package to scan was deleted, was the last to unload
                # and we still have lines to pick
                "start_operation",
                # next "logical" state, when the scan is ok
                "unload_set_destination",
            }
        )

    def unload_scan_destination(self):
        return self._response_schema(
            next_states={
                "unload_single",
                "unload_set_destination",
                "confirm_unload_set_destination",
                "start",
                "start_operation",
            }
        )

    @property
    def _schema_for_batch_details(self):
        return self.schemas.picking_batch(with_pickings=True)

    @property
    def _schema_for_single_line_details(self):
        schema = self.schemas.operation()
        schema["picking"] = self.schemas._schema_dict_of(self.schemas.picking())
        schema["batch"] = self.schemas._schema_dict_of(self.schemas.picking_batch())
        return schema

    @property
    def _schema_for_unload_all(self):
        schema = self.schemas.picking_batch()
        schema["location_dest"] = self.schemas._schema_dict_of(self.schemas.location())
        return schema

    @property
    def _schema_for_unload_single(self):
        schema = self.schemas.picking_batch()
        schema["package"] = self.schemas._schema_dict_of(self.schemas.package())
        schema["location_dest"] = self.schemas._schema_dict_of(self.schemas.location())
        return schema

    @property
    def _schema_for_zero_check(self):
        schema = {
            "id": {"required": True, "type": "integer"},
        }
        schema["location_src"] = self.schemas._schema_dict_of(self.schemas.location())
        schema["batch"] = self.schemas._schema_dict_of(self.schemas.picking_batch())
        return schema

    @property
    def _schema_for_batch_selection(self):
        return self.schemas._schema_search_results_of(self.schemas.picking_batch())
