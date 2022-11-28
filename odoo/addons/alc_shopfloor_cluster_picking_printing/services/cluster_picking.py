# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def put_in_pack(self, picking_batch_id, picking_id, nbr_packages):
        if not self.shopfloor_user.printing_product_label_printer_id:
            return self._response_put_in_pack(
                picking_batch_id,
                message=self.msg_store.no_product_label_printer_found(),
            )
        if not self.shopfloor_user.printing_package_label_printer_id:
            return self._response_put_in_pack(
                picking_batch_id,
                message=self.msg_store.no_package_label_printer_found(),
            )
        return super(ClusterPicking, self).put_in_pack(
            picking_batch_id, picking_id, nbr_packages
        )

    def _put_in_pack(self, picking, nbr_packages):
        pack = super(ClusterPicking, self)._put_in_pack(picking, nbr_packages)
        if pack and self.work.menu.print_on_pack_pickings:
            self._print_picking_med_products_labels(picking, pack)
        return pack

    def scan_destination_pack(
        self, picking_batch_id, operation_id, barcode, quantity, lot_id=None
    ):
        result = super(ClusterPicking, self).scan_destination_pack(
            picking_batch_id, operation_id, barcode, quantity, lot_id
        )
        if result.get("message", {}).get("message_type") == "error":
            return result
        search = self._actions_for("search")
        bin_package = search.package_from_scan(barcode)

        if (
            bin_package
            and bin_package.is_internal
            and not self.work.menu.print_on_pack_pickings
        ):
            batch = self.env["stock.picking.wave"].browse(picking_batch_id)
            if not batch.exists():
                return self._response_batch_does_not_exist()
            operation = self.env["stock.pack.operation"].browse(operation_id)
            if not operation.exists():
                return self._pick_next_operation(
                    batch, message=self.msg_store.operation_not_found()
                )
            lot = self.env["stock.production.lot"].browse(lot_id) if lot_id else None

            if not operation.picking_id.partner_id.no_labels_food_products:
                self._print_picking_food_product_labels(
                    operation, quantity=quantity, lot_id=lot
                )
        return result

    def _print_picking_med_products_labels(self, picking, package):
        picking.sudo().print_products_label(
            printer_id=self.shopfloor_user.printing_product_label_printer_id.id,
            packages=package,
        )
        picking.sudo().print_packages_label(
            printer_id=self.shopfloor_user.printing_package_label_printer_id.id,
            packages=package,
        )

    def _print_picking_food_product_labels(self, operation, quantity=1, lot_id=None):
        # report template relies on quantity_done, but it might not be computed yet
        # when the report is generated.
        # bug observed by Jacques-Etienne and Lindsay who might know more.
        operation.sudo().print_food_product_label(
            printer_id=self.shopfloor_user.printing_product_label_printer_id.id,
            quantity=1,
            quantity_done=quantity,
            lot_id=lot_id,
        )
