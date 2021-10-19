# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import CommonCase, PickingBatchMixin


# pylint: disable=missing-return
class ClusterPickingCommonCase(CommonCase, PickingBatchMixin):
    @classmethod
    def setUpClassVars(cls, *args, **kwargs):
        super(ClusterPickingCommonCase, cls).setUpClassVars(*args, **kwargs)
        cls.menu = cls.env.ref("alc_shopfloor.shopfloor_menu_cluster_picking")
        cls.profile = cls.env.ref("shopfloor_base.profile_demo_1")
        cls.picking_type = cls.menu.picking_type_ids
        cls.wh = cls.picking_type.warehouse_id

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(ClusterPickingCommonCase, cls).setUpClassBaseData(*args, **kwargs)
        cls.wh.sudo().delivery_steps = "pick_pack_ship"

    def setUp(self):
        super(ClusterPickingCommonCase, self).setUp()
        with self.work_on_services(menu=self.menu, profile=self.profile) as work:
            self.service = work.component(usage="cluster_picking")

    def _operation_data(self, operation, qty=None, package_dest=False, force_lot=None):
        picking = operation.picking_id
        # A package exists on the move line, because the quant created
        # by ``_simulate_batch_selected`` has a package.
        operations = self.data.operations(operation)
        data = None
        if force_lot:
            for op in operations:
                if op.get("lot", {}).get("id") == force_lot.id:
                    data = op
                    break
            if not data:
                raise SystemError("Force lot not found into operation")
        else:
            data = operations[0]
        if not package_dest:
            data["package_dest"] = None
        else:
            package_dest = package_dest.with_context(picking_id=operation.picking_id.id)
            data["package_dest"] = self.data.package(
                package_dest, picking=operation.picking_id
            )
        if qty:
            data["quantity"] = qty
        data.update(
            {
                "batch": self.data.picking_batch(picking.batch_id),
                "picking": self.data.picking(picking),
            }
        )
        return data

    @classmethod
    def _set_dest_package_and_done(cls, operations, dest_package):
        """Simulate what would have been done in the previous steps"""
        for operation in operations:
            operation.write(
                {
                    "qty_done": operation.product_qty,
                    "result_package_id": dest_package.id,
                }
            )

    def _data_for_batch(self, batch, location, pack=None):
        data = self.data.picking_batch(batch)
        data["location_dest"] = self.data.location(location)
        if pack:
            data["package"] = self.data.package(pack)
        return data


# pylint: disable=missing-return
class ClusterPickingLineCommonCase(ClusterPickingCommonCase):
    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(ClusterPickingLineCommonCase, cls).setUpClassBaseData(*args, **kwargs)
        # quants already existing are from demo data
        cls.env["stock.quant"].with_context(force_unlink=True).sudo().search(
            [("location_id", "=", cls.stock_location.id)]
        ).unlink()
        cls.batch = cls._create_picking_batch(
            [[cls.BatchProduct(product=cls.product_a, quantity=1)]]
        )

    def _operation_data(self, operation, qty=1.0, package_dest=False, force_lot=None):
        # just force qty to 1.0
        return super(ClusterPickingLineCommonCase, self)._operation_data(
            operation, qty=qty, package_dest=package_dest, force_lot=None
        )
