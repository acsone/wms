# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_rounds.tests.common import DeliverDeliveryRoundTestCase


class TestExcludePickings(DeliverDeliveryRoundTestCase):
    """Test to run at install"""

    @classmethod
    def setUpClass(cls):
        super(TestExcludePickings, cls).setUpClass()
        cls.product_unavailable = cls.env["product.product"].create(
            {
                "name": "Unittest Product Unavailable",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )

    def _process_and_create_backorder(self, picking):
        result = picking.do_new_transfer()
        if result:
            backorder_reason = self.backorder_reason_model.create(
                {"name": "Unittest backorder", "backorder_action_to_do": "create"}
            )
            result = picking.do_new_transfer()
            # Check that the transfer action return the good wizard
            self.assertEqual(result["res_model"], "stock.backorder.choice")
            # Create backorder choice wizard and execute it
            wizard = self.backorder_choice_model.with_context(result["context"]).create(
                {"reason_id": backorder_reason.id}
            )
            wizard.apply()
        return self._get_backorder(picking)

    def _get_backorder(self, picking):
        backorder = picking.browse()
        while True:
            picking = picking.search([("backorder_id", "=", picking.id)])
            if picking:
                backorder = picking
            else:
                break
        return backorder

    def test_backorder_on_bo_product_blocked(self):
        sale1 = self._confirm_sale_order(
            carrier_id=self.delivery_carrier.id,
            product=self.p1,
            qty=self.p1.qty_available * 2,
        )
        # PICK has picking_type.groupbypartner = False  -> 1 by SO
        pick = sale1.picking_ids.filtered(lambda p: p.picking_type_subcode == "PICK")
        pick_out = sale1.picking_ids - pick
        self.assertEqual(len(pick), 1)

        # create the delivery round
        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )

        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign should assign the picking to
        # this new delivery since the product is partially available
        pick.with_context(round_autoset=True)._job_action_assign()
        self.assertEqual(sale1.mapped("picking_ids.delivery_round_id"), delivery_round)

        # If we create a backorder, the picking is not assigned anymore since product
        # are announced as BO
        backorder = self._process_and_create_backorder(pick_out)
        # self.assertEqual(backorder.state, "partially_available")
        pick.with_context(round_autoset=True)._job_action_assign()
        self.assertFalse(backorder.delivery_round_id)
