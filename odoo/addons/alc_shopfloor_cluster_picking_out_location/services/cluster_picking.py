# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def prepare_unload(self, picking_batch_id):
        # # Check that unload might go to unload_single if the option is chosen
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        if not self.work.menu.unload_on_specific_location:
            return super().prepare_unload(picking_batch_id)
        return self._unload_next_package(batch)

    def unload_scan_pack(self, picking_batch_id, package_id, barcode):
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        package_from_id = self.env["stock.quant.package"].browse(package_id)
        if (
            package_from_id.name != barcode
            and self.work.menu.unload_on_specific_location
        ):
            search = self._actions_for("search")
            package = search.package_from_scan(barcode)
            if not package:
                # Response single needs a package id to work.
                # If package does not exist, we loose it in the frontend
                # => keep using package_id that was first provided
                return self._response_for_unload_single(
                    batch,
                    package_from_id,
                    message=self.msg_store.package_does_not_exist(),
                )
            if package.is_scanned:
                return self._response_for_unload_single(
                    batch,
                    package,
                    message=self.msg_store.package_already_scanned(),
                )
            packages = batch.picking_ids.move_line_ids.result_package_id
            if package not in packages:
                return self._response_for_unload_single(
                    batch,
                    package,
                    message=self.msg_store.package_not_in_batch(),
                )
            return self._response_for_unload_set_destination(batch, package)

        return super().unload_scan_pack(picking_batch_id, package_id, barcode)

    def unload_scan_destination(
        self, picking_batch_id, package_id, barcode, confirmation=False
    ):
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        package = self.env["stock.quant.package"].search([("id", "=", package_id)])
        line = self.env["stock.move.line"].search(
            [("result_package_id", "=", package_id)]
        )
        scanned_location = self._actions_for("search").location_from_scan(barcode)
        release_channel = line.mapped("picking_id").release_channel_id
        (
            parent_location,
            existing_release_channel,
        ) = self._get_parent_out_location_and_release_channel(scanned_location)

        if (
            (
                scanned_location.keep_track_of_release_channel
                or parent_location.keep_track_of_release_channel
            )
            and existing_release_channel
            and existing_release_channel != release_channel
        ):
            return self._response_for_unload_set_destination(
                batch, package, message=self.msg_store.out_trolley_blocked_by_delivery()
            )
        res = super().unload_scan_destination(
            picking_batch_id, package_id, barcode, confirmation
        )
        package.sudo().is_scanned = True
        if (
            scanned_location.keep_track_of_release_channel
            or parent_location.keep_track_of_release_channel
        ) and not existing_release_channel:
            parent_location.sudo().write({"release_channel_id": release_channel.id})

        return res

    def _get_parent_out_location_and_release_channel(self, location):
        location = self.env["stock.location"].search(
            [
                ("id", "parent_of", location.id),
                ("keep_track_of_release_channel", "=", True),
            ],
            order="id asc",
            limit=1,
        )

        if location:
            return location, location.release_channel_id
        return None, None
