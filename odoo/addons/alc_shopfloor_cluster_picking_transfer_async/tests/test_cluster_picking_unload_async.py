# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.shopfloor.tests.test_cluster_picking_unload import (
    ClusterPickingUnloadingCommonCase,
)


class TestClusterPickingUnloadAsync(ClusterPickingUnloadingCommonCase):
    """Tests covering the /set_destination_all endpoint.

    All the picked lines go to the same destination, a single call to this
    endpoint set them as "unloaded" and set the destination. When the last
    available line of a picking is unloaded, the picking is set to 'done'.
    """

    def setUp(self):
        super().setUp()
        self.menu.sudo().process_picking_in_background = True

    def test_set_destination_all_ok(self):
        """Set destination on all lines for the full batch and end the process."""
        move_lines = self.move_lines
        # put destination packages, the whole quantity on lines and a similar
        # destination (when /set_destination_all is called, all the lines to
        # unload must have the same destination)
        self._set_dest_package_and_done(move_lines[:2], self.bin1)
        self._set_dest_package_and_done(move_lines[2:], self.bin2)
        move_lines.write({"location_dest_id": self.packing_location.id})
        with trap_jobs() as trap:
            response = self.service.dispatch(
                "set_destination_all",
                params={
                    "picking_batch_id": self.batch.id,
                    "barcode": self.packing_location.barcode,
                },
            )
            # the user can start a new batch immediately
            self.assert_response(
                response,
                next_state="start",
                message={"message_type": "success", "body": "Batch Transfer complete"},
            )
            self.assertEqual(trap.jobs_count(), 2)
            trap.assert_enqueued_job(
                self.two_lines_picking._shopfloor_unload_set_picking_to_done,
                args=(self.two_lines_picking.move_line_ids, False),
            )
            trap.assert_enqueued_job(
                self.one_line_picking._shopfloor_unload_set_picking_to_done,
                args=(self.one_line_picking.move_line_ids, False),
            )
            # since the batch is processed in background, we expect the batch to be done
            # and all pickings to be 'assigned'
            self.assertRecordValues(
                move_lines.picking_id, [{"state": "assigned"}, {"state": "assigned"}]
            )
            self.assertEqual(self.batch.state, "done")
            trap.perform_enqueued_jobs()
        # now all picking should be done
        self.assertRecordValues(
            move_lines.picking_id, [{"state": "done"}, {"state": "done"}]
        )
        self.assertRecordValues(
            move_lines,
            [
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
            ],
        )

    def test_set_destination_all_remaining_lines(self):
        """Set destination on all lines for a part of the batch."""
        # Put destination packages, the whole quantity on lines and a similar
        # destination (when /set_destination_all is called, all the lines to
        # unload must have the same destination).
        # However, we keep a line without qty_done and destination package,
        # so when the dest location is set, the endpoint should route back
        # to the 'start_line' state to work on the remaining line.
        lines_to_unload = self.move_lines[:2]
        self._set_dest_package_and_done(lines_to_unload, self.bin1)
        lines_to_unload.write({"location_dest_id": self.packing_location.id})
        with trap_jobs() as trap:
            response = self.service.dispatch(
                "set_destination_all",
                params={
                    "picking_batch_id": self.batch.id,
                    "barcode": self.packing_location.barcode,
                },
            )
            trap.perform_enqueued_jobs()
        # Since the whole batch is not complete, state should not be done.
        # The picking with one line should be "done" because we unloaded its line.
        # The second one still has a line to pick.
        self.assertRecordValues(self.one_line_picking, [{"state": "done"}])
        self.assertRecordValues(self.two_lines_picking, [{"state": "assigned"}])
        self.assertRecordValues(
            self.move_lines,
            [
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    "state": "done",
                    "picking_id": self.one_line_picking.id,
                    "location_dest_id": self.packing_location.id,
                },
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    # will be done when the second line of the picking is unloaded
                    "state": "assigned",
                    "picking_id": self.two_lines_picking.id,
                    "location_dest_id": self.packing_location.id,
                },
                {
                    "shopfloor_unloaded": False,
                    "qty_done": 0,
                    "state": "assigned",
                    "picking_id": self.two_lines_picking.id,
                    "location_dest_id": self.packing_location.id,
                },
            ],
        )
        self.assertRecordValues(self.batch, [{"state": "in_progress"}])
        self.assertEqual(response.get("next_state"), "start_line")

    def test_set_destination_all_picking_unassigned(self):
        """Set destination on lines for some transfers of the batch.

        The remaining transfers stay as unavailable (confirmed) and are removed
        from the batch when this one is validated.
        The remaining transfers will be processed later in a new batch.
        """
        self.batch.picking_ids.do_unreserve()
        location = self.one_line_picking.location_id
        product = self.one_line_picking.move_ids.product_id
        qty = self.one_line_picking.move_ids.product_uom_qty
        self._update_qty_in_location(location, product, qty)
        self.one_line_picking.action_assign()
        # Prepare lines to process
        lines = self.one_line_picking.move_line_ids
        self._set_dest_package_and_done(lines, self.bin1)
        lines.write({"location_dest_id": self.packing_location.id})

        with trap_jobs() as trap:
            response = self.service.dispatch(
                "set_destination_all",
                params={
                    "picking_batch_id": self.batch.id,
                    "barcode": self.packing_location.barcode,
                },
            )
            # the user can start a new batch immediately
            self.assert_response(
                response,
                next_state="start",
                message={"message_type": "success", "body": "Batch Transfer complete"},
            )
            self.assertEqual(trap.jobs_count(), 3)
            self.assertRecordValues(self.one_line_picking, [{"state": "assigned"}])
            self.assertRecordValues(self.two_lines_picking, [{"state": "confirmed"}])
            trap.assert_enqueued_job(
                self.one_line_picking._shopfloor_unload_set_picking_to_done,
                args=(self.one_line_picking.move_line_ids, False),
            )
            trap.perform_enqueued_jobs()
        # The batch should be done with only one picking.
        # The remaining picking has been removed from the current batch
        self.assertRecordValues(self.one_line_picking, [{"state": "done"}])
        self.assertRecordValues(self.two_lines_picking, [{"state": "confirmed"}])
        self.assertRecordValues(self.batch, [{"state": "done"}])
        self.assertEqual(self.one_line_picking.batch_id, self.batch)
        self.assertFalse(self.two_lines_picking.batch_id)

        self.assert_response(
            response,
            next_state="start",
            message=self.service.msg_store.batch_transfer_complete(),
        )

    def test_set_destination_all_but_different_dest(self):
        """Endpoint was called but destinations are different."""
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines, self.bin1)
        move_lines[:2].write({"location_dest_id": self.packing_a_location.id})
        move_lines[2:].write({"location_dest_id": self.packing_b_location.id})

        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": self.batch.id,
                "barcode": self.packing_location.barcode,
            },
        )
        location = move_lines[0].location_dest_id
        data = self._data_for_batch(self.batch, location, pack=self.bin1)
        self.assert_response(
            response,
            next_state="unload_single",
            data=data,
        )

    def test_set_destination_all_error_location_not_found(self):
        """Endpoint called with a barcode not existing for a location."""
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines, self.bin1)
        move_lines.write({"location_dest_id": self.packing_a_location.id})

        response = self.service.dispatch(
            "set_destination_all",
            params={"picking_batch_id": self.batch.id, "barcode": "NOTFOUND"},
        )
        location = move_lines[0].location_dest_id
        data = self._data_for_batch(self.batch, location)
        self.assert_response(
            response,
            next_state="unload_all",
            data=data,
            message={
                "message_type": "error",
                "body": "No location found for this barcode.",
            },
        )

    def test_set_destination_all_error_location_invalid(self):
        """Endpoint called with a barcode for an invalid location.

        It is invalid when the location is not the destination location or
        sublocation of the picking type.
        """
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines, self.bin1)
        move_lines.write({"location_dest_id": self.packing_a_location.id})

        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": self.batch.id,
                "barcode": self.dispatch_location.barcode,
            },
        )
        location = move_lines[0].location_dest_id
        data = self._data_for_batch(self.batch, location)
        self.assert_response(
            response,
            next_state="unload_all",
            data=data,
            message={"message_type": "error", "body": "You cannot place it here"},
        )

    def test_set_destination_all_error_location_move_invalid(self):
        """Endpoint called with a barcode for an invalid location.

        It is invalid when the location is not a sublocation of the picking
        or move destination
        """
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines, self.bin1)
        move_lines[0].move_id.location_dest_id = self.packing_a_location
        move_lines[0].picking_id.location_dest_id = self.packing_a_location

        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": self.batch.id,
                "barcode": self.packing_b_location.barcode,
            },
        )
        location = move_lines[0].location_dest_id
        data = self._data_for_batch(self.batch, location)
        self.assert_response(
            response,
            next_state="unload_all",
            data=data,
            message=self.service.msg_store.dest_location_not_allowed(),
        )

    def test_set_destination_all_need_confirmation(self):
        """Endpoint called with a barcode for another (valid) location."""
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines, self.bin1)
        move_lines.write({"location_dest_id": self.packing_a_location.id})

        barcode = self.packing_b_location.barcode
        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": self.batch.id,
                "barcode": barcode,
            },
        )
        location = move_lines[0].location_dest_id
        data = self._data_for_batch(self.batch, location)
        data["confirmation"] = barcode
        self.assert_response(
            response,
            next_state="confirm_unload_all",
            data=data,
        )

    def test_set_destination_all_with_confirmation(self):
        """Endpoint called with a barcode for another (valid) location, confirm."""
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines, self.bin1)
        move_lines.write({"location_dest_id": self.packing_a_location.id})

        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": self.batch.id,
                "barcode": self.packing_b_location.barcode,
                "confirmation": self.packing_b_location.barcode,
            },
        )
        self.assertRecordValues(
            move_lines,
            [
                {"location_dest_id": self.packing_b_location.id},
                {"location_dest_id": self.packing_b_location.id},
                {"location_dest_id": self.packing_b_location.id},
            ],
        )
        self.assert_response(
            response,
            next_state="start",
            message={"message_type": "success", "body": "Batch Transfer complete"},
        )

    def _test_line_set_destination_all(
        self,
        move_line,
        expected_batch_state: str,
        expected_next_step: str,
        expected_next_line_id: int = None,
    ):
        self._set_dest_package_and_done(move_line, self.bin1)
        move_line.write({"location_dest_id": self.packing_location.id})

        with trap_jobs() as trap:
            response = self.service.dispatch(
                "set_destination_all",
                params={
                    "picking_batch_id": self.batch.id,
                    "barcode": self.packing_location.barcode,
                },
            )
            trap.perform_enqueued_jobs()

        self.assertRecordValues(self.batch, [{"state": expected_batch_state}])
        self.assertEqual(response.get("next_state"), expected_next_step)
        if expected_next_line_id:
            self.assertEqual(
                response.get("data", {}).get("start_line", {}).get("id"),
                expected_next_line_id,
            )

    def test_set_destination_all_on_line_at_a_time(self):
        """
        Test partial set destination.

        This test ensures that a batch isn't marked as complete until all lines are picked.
        When the user selects "full bin" allowing them to place already picked items
        in a pack to potentially empty the bin and resume where they left off.

        We assume a batch with two pickings and 3 moves.

        1- After unloading the first line, if there are still unpicked items, the batch
        and picking are not considered complete. The user is redirected to the "next line"
        page to pick the remaining items.

        2- Upon unloading the second line, its picking is processed in the background
        and marked as completed with no more items to pick. However, the batch remains
        in progress due to the third item still being unpicked. The user is directed to
        the "next line" page to pick the last line.

        3- When the last item is picked, both the picking and the batch are marked as done.
        The user is then returned to the "start" page to initiate a new batch.
        """
        self.assertEqual(len(self.batch.move_line_ids), 3)
        self._test_line_set_destination_all(
            move_line=self.two_lines_picking.move_line_ids[0],
            expected_batch_state="in_progress",
            expected_next_step="start_line",
            expected_next_line_id=self.two_lines_picking.move_line_ids[1].id,
        )
        self.assertRecordValues(
            self.two_lines_picking, [{"state": "assigned", "batch_id": self.batch.id}]
        )
        self.assertRecordValues(
            self.one_line_picking, [{"state": "assigned", "batch_id": self.batch.id}]
        )
        self._test_line_set_destination_all(
            move_line=self.two_lines_picking.move_line_ids[1],
            expected_batch_state="in_progress",
            expected_next_step="start_line",
            expected_next_line_id=self.one_line_picking.move_line_ids[0].id,
        )
        self.assertRecordValues(
            self.two_lines_picking, [{"state": "done", "batch_id": self.batch.id}]
        )
        self.assertRecordValues(
            self.one_line_picking, [{"state": "assigned", "batch_id": self.batch.id}]
        )
        self._test_line_set_destination_all(
            move_line=self.one_line_picking.move_line_ids[0],
            expected_batch_state="done",
            expected_next_step="start",
        )
        self.assertRecordValues(
            self.two_lines_picking, [{"state": "done", "batch_id": self.batch.id}]
        )
        self.assertRecordValues(
            self.one_line_picking, [{"state": "done", "batch_id": self.batch.id}]
        )

    def test_set_destination_all_on_line_at_a_time_but_not_the_last(self):
        """
        Test partial set destination but not the last item.

        same scenario as the previous test but this time we will not unload the last line
        """
        self.assertEqual(len(self.batch.move_line_ids), 3)
        self._test_line_set_destination_all(
            move_line=self.two_lines_picking.move_line_ids[0],
            expected_batch_state="in_progress",
            expected_next_step="start_line",
            expected_next_line_id=self.two_lines_picking.move_line_ids[1].id,
        )
        self.assertRecordValues(
            self.two_lines_picking, [{"state": "assigned", "batch_id": self.batch.id}]
        )
        self.assertRecordValues(
            self.one_line_picking, [{"state": "assigned", "batch_id": self.batch.id}]
        )
        self._test_line_set_destination_all(
            move_line=self.two_lines_picking.move_line_ids[1],
            expected_batch_state="in_progress",
            expected_next_step="start_line",
            expected_next_line_id=self.one_line_picking.move_line_ids[0].id,
        )
        self.assertRecordValues(
            self.two_lines_picking, [{"state": "done", "batch_id": self.batch.id}]
        )
        self.assertRecordValues(
            self.one_line_picking, [{"state": "assigned", "batch_id": self.batch.id}]
        )
        self.one_line_picking.move_line_ids[0].package_id = self.bin1
        self._test_line_set_destination_all(
            move_line=self.one_line_picking.move_line_ids[0],
            expected_batch_state="done",
            expected_next_step="start",
        )
        self.assertRecordValues(
            self.two_lines_picking, [{"state": "done", "batch_id": self.batch.id}]
        )
        self.assertRecordValues(
            self.one_line_picking, [{"state": "confirmed", "batch_id": False}]
        )
