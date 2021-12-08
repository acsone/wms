# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def _response_for_start_operation(self, operation, message=None, popup=None):
        return self._response(
            next_state="start_operation",
            data=self._data_operation(operation),
            message=message,
            popup=popup,
        )

    def _get_next_picking_to_pack(self, batch):
        """
        Return a picking not yet packed. The returned picking is the first
        one into the list of picking not yet packed (shopfloor_packing_done=Fasle).
         nbr_packages
        """
        pickings_to_pack = batch.picking_ids.filtered(
            lambda p: not p.shopfloor_packing_done
        )
        operations = pickings_to_pack.mapped("pack_operation_ids")
        operations = operations.sorted(key=lambda op: op.result_package_id.name)
        return operations[0].picking_id

    def _response_pack_picking(self, batch, message=None):
        picking = self._get_next_picking_to_pack(batch)
        data = self.data_detail.picking_detail(picking)
        return self._response(next_state="pack_picking", data=data, message=message)

    def scan_destination_pack(
        self, picking_batch_id, operation_id, barcode, quantity, lot_id=None
    ):
        search = self._actions_for("search")
        bin_package = search.package_from_scan(barcode)

        if bin_package and not bin_package.is_internal:
            batch = self.env["stock.picking.wave"].browse(picking_batch_id)
            if not batch.exists():
                return self._response_batch_does_not_exist()
            operation = self.env["stock.pack.operation"].browse(operation_id)
            if not operation.exists():
                return self._pick_next_operation(
                    batch, message=self.msg_store.operation_not_found()
                )
            return self._response_for_scan_destination(
                operation, message=self.msg_store.bin_should_be_internal(bin_package)
            )
        return super(ClusterPicking, self).scan_destination_pack(
            picking_batch_id, operation_id, barcode, quantity, lot_id
        )

    def prepare_unload(self, picking_batch_id):
        # before initializing the unloading phase we put picking in pack if
        # required by the scenario
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        if not self.work.menu.pack_pickings or batch.shopfloor_packing_done:
            return super(ClusterPicking, self).prepare_unload(picking_batch_id)
        return self._response_pack_picking(batch)

    def put_in_pack(self, picking_batch_id, picking_id, nbr_packages):
        batch = self.env["stock.picking.wave"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        picking = batch.picking_ids.filtered(
            lambda p, picking_id=picking_id: p.id == picking_id
        )
        if not picking:
            return self._response_put_in_pack(
                picking_batch_id, message=self.msg_store.dstock_picking_not_found(),
            )
        if picking.shopfloor_packing_done:
            return self._response_put_in_pack(
                picking_batch_id,
                message=self.msg_store.stock_picking_already_packed(picking),
            )
        if nbr_packages <= 0:
            return self._response_put_in_pack(
                picking_batch_id,
                message=self.msg_store.nbr_packages_must_be_greated_than_zero(),
            )
        savepoint = self._actions_for("savepoint").new()
        pack = self._put_in_pack(picking, nbr_packages)
        if not pack:
            savepoint.rollback()
            return self._response_put_in_pack(
                picking_batch_id,
                message=self.msg_store.notable_to_put_in_pack(picking),
            )
        return self._response_put_in_pack(picking_batch_id)

    def _put_in_pack(self, picking, nbr_packages):
        pack = picking.put_in_pack()
        picking.shopfloor_packing_done = True
        if (
            isinstance(pack, dict)
            and pack.get("res_model") == "stock.quant.package"
            and pack.get("res_id")
        ):
            pack = self.env["stock.quant.package"].browse(pack.get("res_id"))
        if isinstance(pack, self.env["stock.quant.package"].__class__):
            pack.nbr_packages = nbr_packages
        return pack

    def _response_put_in_pack(self, picking_batch_id, message=None):
        res = self.prepare_unload(picking_batch_id)
        if message:
            res["message"] = message
        return res


class ShopfloorClusterPickingValidator(Component):
    """Validators for the Cluster Picking endpoints"""

    _inherit = "shopfloor.cluster_picking.validator"

    def put_in_pack(self):
        return {
            "picking_batch_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "picking_id": {"coerce": to_int, "required": True, "type": "integer"},
            "nbr_packages": {"coerce": to_int, "required": True, "type": "integer"},
        }


class ShopfloorClusterPickingValidatorResponse(Component):
    """Validators for the Cluster Picking endpoints responses"""

    _inherit = "shopfloor.cluster_picking.validator.response"

    def _states(self):
        states = super(ShopfloorClusterPickingValidatorResponse, self)._states()
        states["pack_picking"] = self._schema_pack_picking
        return states

    @property
    def _schema_pack_picking(self):
        schema = self.schemas_detail.picking_detail()
        return {"type": "dict", "nullable": True, "schema": schema}

    def prepare_unload(self):
        res = super(ShopfloorClusterPickingValidatorResponse, self).prepare_unload()
        res["data"]["schema"]["pack_picking"] = self._schema_pack_picking
        return res

    def put_in_pack(self):
        return self.prepare_unload()

    def confirm_start(self):
        res = super(ShopfloorClusterPickingValidatorResponse, self).confirm_start()
        res["data"]["schema"]["pack_picking"] = self._schema_pack_picking
        return res
