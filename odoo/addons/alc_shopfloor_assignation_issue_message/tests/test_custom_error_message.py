# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_shopfloor.tests.test_location_content_transfer_base import (
    LocationContentTransferCommonCase,
)


class TestCustomErrorMessage(LocationContentTransferCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestCustomErrorMessage, cls).setUpClass()
        cls.picking = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)],
        )

        cls._fill_stock_for_moves(
            cls.picking.move_lines, location=cls.content_loc, in_package=True
        )
        cls.picking.action_assign()
        cls.products = cls.product_a | cls.product_b
        cls.putway = (
            cls.env["product.putaway"]
            .sudo()
            .create(
                {
                    "name": "test",
                    "method": "fixed",
                    "fixed_location_ids": [
                        (
                            0,
                            0,
                            {"category_id": c.id, "fixed_location_id": cls.shelf1.id},
                        )
                        for c in cls.products.sudo().mapped("categ_id")
                    ],
                }
            )
        )
        cls.stock_location.sudo().putaway_strategy_id = cls.putway

    def test_00_trigger_custom_message_reserved_moves(self):
        # Picking was assigned, we reverse the assignation but keep the moves reserved
        self.picking.pack_operation_ids.unlink()

        product_templates_names = self.products.mapped("product_tmpl_id.name")
        response = self.service.dispatch(
            "scan_location", params={"barcode": self.content_loc.barcode}
        )
        self.assert_response_start(
            response,
            message=self.service.msg_store.reserved_moves_in_current_location(
                self.content_loc, product_templates_names, self.picking
            ),
        )
