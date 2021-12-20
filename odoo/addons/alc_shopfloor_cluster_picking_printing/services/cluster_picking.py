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
            self._print_picking_labels(picking, pack)
        return pack

    def _print_picking_labels(self, picking, package):
        picking.sudo().print_products_label(
            printer_id=self.shopfloor_user.printing_product_label_printer_id.id,
            packages=package,
        )
        picking.sudo().print_packages_label(
            printer_id=self.shopfloor_user.printing_package_label_printer_id.id,
            packages=package,
        )
