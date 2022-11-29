# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_shopfloor.tests.test_cluster_picking_stock_issue import (
    ClusterPickingStockIssue,
)
from odoo.addons.product_additional.tests.common import StockPickingTestCase


class TestClusterPickingStockIssueProductAdditional(
    ClusterPickingStockIssue, StockPickingTestCase
):
    @classmethod
    def setUpClass(cls):
        super(TestClusterPickingStockIssueProductAdditional, cls).setUpClass()
        cls.dest_package = cls.env["stock.quant.package"].create({})

    def _create_batch_additional_products(self, products, qty):
        sale = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner1.id,
                    "warehouse_id": self.warehouse_1.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom_qty": qty,
                                "product_uom": product.uom_id.id,
                                "price_unit": 1,
                            },
                        )
                        for product in products
                    ],
                }
            )
        )
        sale.action_confirm()
        pick = self._get_picking_pick(sale)
        batch = self.env["stock.picking.wave"].create(
            {"picking_ids": [(6, None, pick.ids)]}
        )
        batch.picking_ids.action_confirm()
        batch.picking_ids.action_assign()
        return batch

    def test_stock_issue_product_additional(self):

        self._update_qty_in_location(self.shelf1, self.main_product, 20)
        self._update_qty_in_location(self.shelf2, self.additional_product, 50)
        self.batch_additional_product = self._create_batch_additional_products(
            [self.main_product], qty=3
        )
        self._simulate_batch_selected(self.batch_additional_product, fill_stock=False)
        main_move = self.batch_additional_product.picking_ids.mapped(
            "move_lines"
        ).filtered(lambda m: not m.is_additional_move)
        additional_move = self.batch_additional_product.picking_ids.mapped(
            "move_lines"
        ).filtered(lambda m: m.is_additional_move)
        self._set_dest_package_and_done(main_move.pack_operation_ids, self.dest_package)
        self._stock_issue(additional_move.pack_operation_ids)
        self.assert_stock_issue_reserved_qties(
            additional_move.picking_id, self.shelf2, additional_move.product_id, 0
        )

    def test_stock_issue_product_additional_partial_picking(self):

        self._update_qty_in_location(self.shelf1, self.main_product, 20)
        self._update_qty_in_location(self.shelf2, self.additional_product, 50)
        self.batch_additional_product = self._create_batch_additional_products(
            [self.main_product], qty=3
        )
        self._simulate_batch_selected(self.batch_additional_product, fill_stock=False)
        main_move = self.batch_additional_product.picking_ids.mapped(
            "move_lines"
        ).filtered(lambda m: not m.is_additional_move)
        additional_move = self.batch_additional_product.picking_ids.mapped(
            "move_lines"
        ).filtered(lambda m: m.is_additional_move)
        self._set_dest_package_and_done(main_move.pack_operation_ids, self.dest_package)

        operation_shelf2 = additional_move.pack_operation_ids.filtered(
            lambda l: l.location_id == self.shelf2
        )
        self.service.scan_destination_pack(
            self.batch.id, operation_shelf2.id, self.dest_package.name, 3
        )
        self._stock_issue(operation_shelf2)
        self.assert_stock_issue_reserved_qties(
            additional_move.picking_id, self.shelf2, additional_move.product_id, 0
        )
