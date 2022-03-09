# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def scan_workstation(self, picking_batch_id=None, barcode=None):
        if barcode:
            ws = self.env["shopfloor.workstation"].search([("barcode", "=", barcode)])
            batch = self.env["stock.picking.wave"].browse(picking_batch_id)
            if ws:
                ws.set_as_default_on_user(self.shopfloor_user.sudo())
                batch.write({"workstation_id": ws.id})
                message = self.msg_store.workstation_set(ws)
                return super(ClusterPicking, self)._prepare_pack_picking(
                    batch, message=message
                )
            message = self.msg_store.workstation_not_found()
            return self._response(next_state="scan_workstation", message=message)
        return self._response(next_state="scan_workstation")

    def prepare_unload(self, picking_batch_id):
        # # We chose the workstation before starting to unload
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        if not self.work.menu.scan_workstation or batch.workstation_selected:
            return super(ClusterPicking, self).prepare_unload(picking_batch_id)
        return self.scan_workstation(picking_batch_id)


class ShopfloorClusterPickingValidator(Component):
    """Validators for the Cluster Picking endpoints"""

    _inherit = "shopfloor.cluster_picking.validator"

    def scan_workstation(self):
        return {
            "barcode": {"required": False, "type": "string"},
            "picking_batch_id": {"required": True, "type": "integer"},
        }


class ShopfloorClusterPickingValidatorResponse(Component):
    """Validators for the Cluster Picking endpoints responses"""

    _inherit = "shopfloor.cluster_picking.validator.response"

    def scan_workstation(self):
        return self._response_schema(
            next_states={"scan_workstation", "pack_picking_scan_pack"}
        )

    @property
    def _schema_worsktation(self):
        schema = self.schemas_detail.workstation_detail()
        return {"type": "dict", "nullable": True, "schema": schema}

    def _states(self):
        states = super(ShopfloorClusterPickingValidatorResponse, self)._states()
        states["scan_workstation"] = self.schemas_detail.workstation_detail()
        return states

    def confirm_start(self):
        res = super(ShopfloorClusterPickingValidatorResponse, self).confirm_start()
        res["data"]["schema"]["scan_workstation"] = self._schema_worsktation
        return res

    def scan_destination_pack(self):
        res = super(
            ShopfloorClusterPickingValidatorResponse, self
        ).scan_destination_pack()
        res["data"]["schema"]["scan_workstation"] = self._schema_worsktation
        return res
