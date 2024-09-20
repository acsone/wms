# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def put_in_pack(
        self, picking_batch_id, picking_id, nbr_packages=None, package_type_id=None
    ):
        if not self.env.user.printing_product_label_printer_id:
            return self._response_put_in_pack(
                picking_batch_id,
                message=self.msg_store.no_product_label_printer_found(),
            )
        if not self.env.user.default_label_printer_id:
            return self._response_put_in_pack(
                picking_batch_id,
                message=self.msg_store.no_package_label_printer_found(),
            )
        return super().put_in_pack(
            picking_batch_id,
            picking_id,
            nbr_packages=nbr_packages,
            package_type_id=package_type_id,
        )

    def _postprocess_put_in_pack(self, picking, pack):
        res = super()._postprocess_put_in_pack(picking, pack)
        if pack and self.work.menu.print_on_pack_pickings:
            self._print_picking_med_products_labels(picking, pack)
        return res

    def scan_destination_pack(self, picking_batch_id, move_line_id, barcode, quantity):
        result = super().scan_destination_pack(
            picking_batch_id, move_line_id, barcode, quantity
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
            batch = self.env["stock.picking.batch"].browse(picking_batch_id)
            if not batch.exists():
                return self._response_batch_does_not_exist()
            move_line = self.env["stock.move.line"].browse(move_line_id)
            if not move_line.exists():
                return self._pick_next_line(
                    batch, message=self.msg_store.operation_not_found()
                )
            lot = move_line.lot_id
            do_not_print_food_labels = (
                move_line.picking_id.partner_id.no_labels_food_products
            )
            self._print_picking_food_product_labels(
                move_line,
                quantity=quantity,
                lot_id=lot,
                do_not_print_food_labels=do_not_print_food_labels,
            )
        return result

    def _print_picking_med_products_labels(self, picking, package):
        picking.sudo().print_products_label(
            printer_id=self.env.user.printing_product_label_printer_id.id,
            packages=package,
        )
        picking.sudo().print_packages_label(
            printer_id=self.env.user.default_label_printer_id.id,
            packages=package,
        )

    def _print_picking_food_product_labels(
        self, move_line, quantity=1, lot_id=None, do_not_print_food_labels=False
    ):
        # report template relies on quantity_done, but it might not be computed yet
        # when the report is generated.
        # bug observed by Jacques-Etienne and Lindsay who might know more.
        if self.env.context.get("test__ignore_label_print"):
            return
        if do_not_print_food_labels:
            if not move_line.picking_id.printed_once:
                move_line.sudo().print_food_product_label(
                    printer_id=self.env.user.printing_product_label_printer_id.id,
                    quantity=1,
                    quantity_done=quantity,
                    lot_id=lot_id,
                    do_not_print_food_labels=do_not_print_food_labels,
                )
            move_line.picking_id.printed_once = True
        else:
            move_line.sudo().print_food_product_label(
                printer_id=self.env.user.printing_product_label_printer_id.id,
                quantity=1,
                quantity_done=quantity,
                lot_id=lot_id,
            )

    def _put_in_pack(self, picking, number_of_parcels, package_type_id):
        pack = super()._put_in_pack(picking, number_of_parcels, package_type_id)
        if isinstance(pack, self.env["stock.quant.package"].__class__):
            if package_type_id is not None:
                # Package type has been chosen by user, so don't override it as
                # it contains already the number of parcels
                return pack
            pack.package_type_id = self._get_suitable_package_type(number_of_parcels)
            pack.number_of_parcels = number_of_parcels
        return pack

    def _get_suitable_package_type(self, number_of_parcels):
        return self.env["stock.package.type"].search(
            [
                ("number_of_parcels", "=", number_of_parcels),
                ("package_carrier_type", "=", "none"),
            ],
            limit=1,
        )
