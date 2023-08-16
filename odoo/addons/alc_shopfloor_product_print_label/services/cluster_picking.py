# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class ClusterPicking(Component):

    _inherit = "shopfloor.cluster.picking"

    def _response_for_print_label(self, move_line, message=None, popup=None):
        return self._response(
            next_state="start_line",
            data=self._data_move_line(move_line),
            message=message,
            popup=popup,
        )

    def print_label(self, picking_batch_id, move_line_id, lot_id=None, printer_id=None):
        lot = None
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        move_line = self.env["stock.move.line"].browse(move_line_id)
        if not move_line.exists():
            return self._pick_next_line(
                batch, message=self.msg_store.operation_not_found()
            )
        printer_id = printer_id or self.env.user.printing_product_label_printer_id.id
        if lot_id:
            lot = self.env["stock.lot"].browse(lot_id)
        if self.work.menu.food_label:
            # We force the print : just need one label
            do_not_print_food_labels = (
                move_line.picking_id.partner_id.no_labels_food_products
            )
            move_line.sudo().print_food_product_label(
                printer_id=printer_id,
                lot_id=lot,
                do_not_print_food_labels=do_not_print_food_labels,
            )

        if self.work.menu.med_label:
            if lot:
                lot.print_lot_label(printer_id=printer_id)
            else:
                move_line.product_id.print_product_label(printer_id=printer_id)

        return self._response_for_print_label(
            move_line, message=self.msg_store.confirm_print_label()
        )


class ShopfloorClusterPickingValidator(Component):
    """Validators for the Cluster Picking endpoints."""

    _inherit = "shopfloor.cluster_picking.validator"
    _usage = "cluster_picking.validator"

    def print_label(self):
        return {
            "picking_batch_id": {"coerce": to_int, "required": True, "type": "integer"},
            "move_line_id": {"coerce": to_int, "required": True, "type": "integer"},
            "lot_id": {"coerce": to_int, "required": False, "type": "integer"},
        }


class ShopfloorClusterPickingValidatorResponse(Component):
    """Validators for the Cluster Picking endpoints responses."""

    _inherit = "shopfloor.cluster_picking.validator.response"
    _usage = "cluster_picking.validator.response"

    def print_label(self):
        return self._response_schema(next_states={"start_line"})
