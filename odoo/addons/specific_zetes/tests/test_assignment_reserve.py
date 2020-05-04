# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_assignment import Assignment
from ..tools.domain_interface import Parameters
from .zetes_test_classes import ZetesReserveTest

OPERATOR_CODE = "99"


class TestAssignemnt(ZetesReserveTest):
    post_install = True
    at_install = False

    def test_01_requ_assignment(self):
        # Check with no current picking
        domain = Assignment(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "Cri01": self.picking_zone_medoc.code,
                "Cri02": None,
                "assignmentType": constants.REASSORT_ASSIGNMENT,
                "requestType": "1",
            }
        )

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, "1")  # Nbr of lines

        # Inventory desactivated
        # # Try to create an inventory for the product 1
        # # This picking should be not available
        # inventory = self.env['stock.inventory'].create({
        #     'name': 'Test',
        #     'filter': 'partial',
        # })
        # inventory.line_ids.create({
        #     'inventory_id': inventory.id,
        #     'product_id': self.product_1.id,
        #     'product_qty': 20,
        #     'location_id': self.env.ref('stock.stock_location_stock').id
        # })
        # # Start the inventory
        # inventory.action_start()
        # result_str = domain.requ(request_params)
        # result = self.format_result(result_str)
        # self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))

        # # Now validate the inventory
        # inventory.action_done()
        # result_str = domain.requ(request_params)
        # result = self.format_result(result_str)
        # self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

    def test_02_requ_assignment(self):
        report_query = """
        SELECT report.id
        FROM report_stock_refill_reassort AS report
          LEFT JOIN stock_location ON stock_location.id = report.location_id
          LEFT JOIN picking_zone
            ON stock_location.picking_zone_id = picking_zone.id
        WHERE report.product_id = %s
          AND picking_zone.code = %s
          AND NOT EXISTS (SELECT 1
                          FROM stock_inventory_line AS sil
                            INNER JOIN stock_inventory AS si
                              ON sil.inventory_id = si.id
                          WHERE si.state = 'confirm'
                          AND sil.location_id = report.location_id)
        LIMIT 1
        """

        # Try to create an inventory for the product 1
        # No product should be available
        inventory = self.env["stock.inventory"].create(
            {"name": "Test", "filter": "partial"}
        )
        inventory.line_ids.create(
            {
                "inventory_id": inventory.id,
                "product_id": self.product_1.id,
                "product_qty": 20,
                "location_id": self.reserve_medoc.id,
            }
        )
        # Start the inventory
        inventory.action_start()
        self.env.cr.execute(
            report_query, (self.product_1.id, self.picking_zone_medoc.code)
        )
        result = self.env.cr.fetchone()
        self.assertFalse(result)

        # Now validate the inventory
        # The product 1 should now be available
        inventory.action_done()
        self.env.cr.execute(
            report_query, (self.product_1.id, self.picking_zone_medoc.code)
        )
        result = self.env.cr.fetchone()
        self.assertTrue(result)
        report_id = result[0]

        model_name = "report.stock.refill.reassort"
        report = self.env[model_name].browse(report_id)
        # Create the picking
        picking = report.create_picking()

        self.assertEqual(
            picking.picking_type_id.zetes_picking_type, constants.REASSORT_ASSIGNMENT
        )

        # Check with no current picking
        domain = Assignment(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "Cri01": self.picking_zone_medoc.code,
                "Cri02": None,
                "assignmentType": constants.REASSORT_ASSIGNMENT,
                "requestType": "1",
            }
        )

        self.assertEqual(
            picking.picking_type_id.zetes_picking_type, constants.REASSORT_ASSIGNMENT
        )

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, "1")  # Nbr of lines
        self.assertEqual(result.groupNum, str(picking.id))
