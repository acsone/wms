# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_shopfloor.tests.test_location_content_transfer_base import (
    LocationContentTransferCommonCase,
)


class TestLocationContentTransferRefill(LocationContentTransferCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestLocationContentTransferRefill, cls).setUpClass()
        cls.env["alc.average.daily.sale"].sudo().refresh_view()
        cls.picking1 = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )
        cls.picking2 = cls._create_picking(
            lines=[(cls.product_c, 10), (cls.product_d, 10)]
        )
        cls.pickings = cls.picking1 | cls.picking2
        cls._fill_stock_for_moves(
            cls.picking1.move_lines, in_package=True, location=cls.content_loc
        )
        cls._fill_stock_for_moves(cls.picking2.move_lines, location=cls.content_loc)
        cls.pickings.action_assign()

    @classmethod
    def _get_rearrange(cls):
        report_query = """
        SELECT report.id, report.location_id
        FROM report_stock_refill_arrange AS report
          LEFT JOIN stock_location ON stock_location.id = report.location_id
        WHERE report.product_id = %s
          AND NOT EXISTS (SELECT 1
                          FROM stock_inventory_line AS sil
                            INNER JOIN stock_inventory AS si
                              ON sil.inventory_id = si.id
                          WHERE si.state = 'confirm'
                          AND sil.location_id = report.location_id)
        LIMIT 1
        """
        cls.content_loc.kind = "parking"
        cls.content_loc.barcode_picking_type_id = cls.picking_type.id
        product = cls.env["product.product"].create(
            {
                "name": "Unittest Product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        inventory = cls.env["stock.inventory"].create(
            {"name": "Test", "filter": "partial"}
        )
        inventory.line_ids.create(
            {
                "inventory_id": inventory.id,
                "product_id": product.id,
                "product_qty": 20,
                "location_id": cls.content_loc.id,
            }
        )
        # Start the inventory
        inventory.action_start()
        inventory.action_done()
        cls.env.cr.execute(report_query, (product.id,))
        result = cls.env.cr.fetchone()
        report_id = result[0]
        report = cls.env["report.stock.refill.arrange"].browse(report_id)
        return report

    @classmethod
    def _get_reassort(cls):
        report_query = """
        SELECT report.id, report.location_id
        FROM report_stock_refill_reassort AS report
          LEFT JOIN stock_location ON stock_location.id = report.location_id
        WHERE report.product_id = %s
          AND NOT EXISTS (SELECT 1
                          FROM stock_inventory_line AS sil
                            INNER JOIN stock_inventory AS si
                              ON sil.inventory_id = si.id
                          WHERE si.state = 'confirm'
                          AND sil.location_id = report.location_id)
        LIMIT 1
        """
        cls.content_loc.kind = "reserve"
        cls.content_loc.barcode_picking_type_id = cls.picking_type.id
        product = cls.env["product.product"].create(
            {
                "name": "Unittest Product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        inventory = cls.env["stock.inventory"].create(
            {"name": "Test", "filter": "partial"}
        )
        inventory.line_ids.create(
            {
                "inventory_id": inventory.id,
                "product_id": product.id,
                "product_qty": 20,
                "location_id": cls.content_loc.id,
            }
        )
        # Start the inventory
        inventory.action_start()
        inventory.action_done()
        cls.env.cr.execute(report_query, (product.id,))
        result = cls.env.cr.fetchone()
        report_id = result[0]
        report = cls.env["report.stock.refill.reassort"].browse(report_id)
        return report

    def test_refill_started_for_current_user_will_be_recovered(self):
        self._simulate_pickings_selected(self.pickings)
        # all lines go to the same destination (shelf1)
        self.assertEqual(
            len(self.pickings.mapped("pack_operation_ids.location_dest_id")), 1
        )
        response = self.service.dispatch("start_or_recover", params={})
        self.assert_response_scan_destination_all(
            response,
            self.pickings,
            message=self.service.msg_store.recovered_previous_session(),
        )

    def test_no_refill_todo(self):
        response = self.service.dispatch("get_work", params={})
        self.assert_response(
            response,
            message=self.service.msg_store.location_content_transfer_no_work(),
            next_state="start",
        )

    def test_refill_todo(self):
        self._get_rearrange()
        response = self.service.dispatch("get_work", params={})
        pickings = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.picking_type.id)]
        )
        self.assert_response_scan_destination_all(response, pickings)

    def test_reassort_todo(self):
        self._get_reassort()
        response = self.service.dispatch("get_work", params={})
        pickings = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.picking_type.id)]
        )
        self.assert_response_scan_destination_all(response, pickings)
