# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def prepare_unload(self, picking_batch_id):
        # # Check that unload might go to unload_single if the option is chosen
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        if not self.work.menu.unload_on_specific_location:
            return super(ClusterPicking, self).prepare_unload(picking_batch_id)
        return self._unload_next_package(batch)

    def unload_scan_pack(self, picking_batch_id, package_id, barcode):
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
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
                    batch, package, message=self.msg_store.package_already_scanned(),
                )
            packages = batch.picking_ids.mapped("pack_operation_ids.result_package_id")
            if package not in packages:
                return self._response_for_unload_single(
                    batch, package, message=self.msg_store.package_not_in_batch(),
                )
            return self._response_for_unload_set_destination(batch, package)

        return super(ClusterPicking, self).unload_scan_pack(
            picking_batch_id, package_id, barcode
        )

    def unload_scan_destination(
        self, picking_batch_id, package_id, barcode, confirmation=False
    ):
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        package = self.env["stock.quant.package"].search([("id", "=", package_id)])
        operation = self.env["stock.pack.operation"].search(
            [("result_package_id", "=", package_id)]
        )
        scanned_location = self._actions_for("search").location_from_scan(barcode)
        delivery_round = operation.mapped("picking_id").delivery_round_id
        (
            parent_location,
            existing_delivery_round,
        ) = self._get_parent_out_location_and_delivery_round(scanned_location)

        if (
            (
                scanned_location.keep_track_of_delivery_round
                or parent_location.keep_track_of_delivery_round
            )
            and existing_delivery_round
            and existing_delivery_round != delivery_round
        ):
            return self._response_for_unload_set_destination(
                batch, package, message=self.msg_store.out_trolley_blocked_by_delivery()
            )
        res = super(ClusterPicking, self).unload_scan_destination(
            picking_batch_id, package_id, barcode, confirmation
        )
        package.sudo().is_scanned = True
        if (
            scanned_location.keep_track_of_delivery_round
            or parent_location.keep_track_of_delivery_round
        ) and not existing_delivery_round:
            parent_location.sudo().write({"delivery_round_id": delivery_round.id})

        return res

    def _get_parent_out_location_and_delivery_round(self, location):
        location_id = None
        delivery_round_id = None
        query = """
                SELECT id, delivery_round_id FROM stock_location
                WHERE parent_left <= %(parent_left)s AND parent_right >= %(parent_right)s
                AND keep_track_of_delivery_round=true
                ORDER BY id ASC
                LIMIT 1
        """
        args = {
            "parent_left": location.parent_left,
            "parent_right": location.parent_right,
        }

        self.env.cr.execute(query, args)
        result = self.env.cr.fetchone()
        if result:
            location_id = result[0]
            delivery_round_id = result[1]

        return (
            self.env["stock.location"].browse(location_id),
            self.env["round.instance"].browse(delivery_round_id),
        )
