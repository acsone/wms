# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_shopfloor.tests.test_cluster_picking_base import (
    ClusterPickingCommonCase,
)


class TestStockIssueOnAllProducts(ClusterPickingCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockIssueOnAllProducts, cls).setUpClass()
        cls.product_a = (
            cls.env["product.product"]
            .sudo()
            .create({"name": "Product A", "type": "product"})
        )
        cls.batch = cls._create_picking_batch(
            [[cls.BatchProduct(product=cls.product_a, quantity=1)]]
        )

    def test_all_products_are_out_of_stock_with_scan_workstation(self):
        self.menu.sudo().scan_workstation = True
        self._update_qty_in_location(self.shelf1, self.product_a, 100)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        operation = self.batch.mapped("picking_ids.move_lines")[0].pack_operation_ids
        params = {"picking_batch_id": self.batch.id, "operation_id": operation.id}

        response = self.service.dispatch("stock_issue", params=params)
        self.assert_response(
            response,
            next_state="start",
            message=self.msg_store.all_waiting_availability(),
        )

    def test_all_products_are_out_of_stock_without_scan_workstation(self):
        self.menu.sudo().scan_workstation = False
        self._update_qty_in_location(self.shelf1, self.product_a, 100)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        operation = self.batch.mapped("picking_ids.move_lines")[0].pack_operation_ids
        params = {"picking_batch_id": self.batch.id, "operation_id": operation.id}

        response = self.service.dispatch("stock_issue", params=params)
        self.assert_response(
            response,
            next_state="start",
            message=self.msg_store.all_waiting_availability(),
        )
