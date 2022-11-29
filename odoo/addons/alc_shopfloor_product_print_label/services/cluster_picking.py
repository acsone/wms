# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class ClusterPicking(Component):

    _inherit = "shopfloor.cluster.picking"

    def _response_for_print_label(self, operation, message=None, popup=None):
        return self._response(
            next_state="start_operation",
            data=self._data_operation(operation),
            message=message,
            popup=popup,
        )

    def print_label(self, picking_batch_id, operation_id, lot_id=None, printer_id=None):
        lot = None
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        operation = self.env["stock.pack.operation"].browse(operation_id)
        if not operation.exists():
            return self._pick_next_operation(
                batch, message=self.msg_store.operation_not_found()
            )
        printer_id = (
            printer_id or self.shopfloor_user.printing_product_label_printer_id.id
        )
        if lot_id:
            lot = self.env["stock.production.lot"].browse(lot_id)
        food_profile = self.env.ref("alc_shopfloor.shopfloor_profile_ali")
        med_profile = self.env.ref("alc_shopfloor.shopfloor_profile_medoc")
        if self.work.menu.profile_id == food_profile:
            # We force the print : just need one label
            do_not_print_food_labels = (
                operation.picking_id.partner_id.no_labels_food_products
            )
            operation.sudo().print_food_product_label(
                printer_id=printer_id,
                lot_id=lot,
                do_not_print_food_labels=do_not_print_food_labels,
            )

        if self.work.menu.profile_id == med_profile:
            if lot:
                lot.print_lot_label(printer_id=printer_id)
            else:
                operation.product_id.print_product_label(printer_id=printer_id)

        return self._response_for_print_label(
            operation, message=self.msg_store.confirm_print_label()
        )


class ShopfloorClusterPickingValidator(Component):
    """Validators for the Cluster Picking endpoints"""

    _inherit = "shopfloor.cluster_picking.validator"
    _usage = "cluster_picking.validator"

    def print_label(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "operation_id": {"coerce": to_int, "required": True, "type": "integer"},
            "lot_id": {"coerce": to_int, "required": False, "type": "integer"},
        }


class ShopfloorClusterPickingValidatorResponse(Component):
    """Validators for the Cluster Picking endpoints responses"""

    _inherit = "shopfloor.cluster_picking.validator.response"
    _usage = "cluster_picking.validator.response"

    def print_label(self):
        return self._response_schema(next_states={"start_operation"})
