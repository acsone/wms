# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_rounds.tests.common import DeliverDeliveryRoundTestCase


class TestExcludePickings(DeliverDeliveryRoundTestCase):
    """Test to run at install
    """

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

    def test_assign_on_so_confirm(self):
        """In this test we check that moves for so line with unavailable qties
        can't be delivered if alone
        """

        # we create the delivery round for the same template as the one linked
        # to the carrier
        self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )
        sale1 = self._confirm_sale_order(
            carrier_id=self.delivery_carrier.id, product=self.product_unavailable
        )

        # at this stage, the pick is not part of the delivery since it's alone...
        # and the product is not available
        pick1 = sale1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertFalse(pick1.delivery_round_id)

        self.assertTrue(pick1.move_lines.delivery_requires_other_lines)
