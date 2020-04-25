# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import common


class TestDeliveryRound(common.DeliveryRoundTestCase):
    """Test to run at install
    """

    @classmethod
    def setUpClass(cls):
        super(TestDeliveryRound, cls).setUpClass()
        # part of the specific modules of Alcyon hard code the Stock location
        # to be ref('stock.stock_location_stock') -> we cannot use another
        # warehouse if we want to use these modules in our test (and we do)
        cls.warehouse_1 = cls.env.ref('stock.warehouse0')
        cls.warehouse_1.write(
            {
                'name': 'Test Warehouse',
                'reception_steps': 'one_step',
                'delivery_steps': 'pick_ship',
                'code': 'TST',
            }
        )
        cls.warehouse_1.pick_type_id.subcode = 'PICK'
        cls.warehouse_1.pick_type_id.groupbypartner = False
        cls.warehouse_1.out_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.create_invoice_on_transfer = True

        # we create a template but without delivery round instante
        cls.delivery_template_2 = cls.env['round.template'].create(
            {'name': 'Unittest delivery template 2'}
        )

        cls.delivery_carrier = cls.env['delivery.carrier'].create(
            {
                'name': 'Unittest shipping costs',
                'delivery_type': 'fixed',
                'fixed_price': 10.0,
                'delivery_template_id': cls.delivery_template_2.id,
            }
        )
        cls.delivery_round_1.state = 'draft'

    def test_picking_assign_00(self):
        """
        Data:
            2 SO for :
              the same partner
              the same carrier
            The carrier is linked to a delivery template without instances
            The SO are confirmed with delivery_step pic + ship
            The outgoing picking is groupbypartner
        Test Case:
            Create a delivery round
            Assign the 2 pickings
        Expected results:
            The pickings are into the round
            The 2 pickings PICK are available
            The 2 SO SHIP are into the same shipping
        """
        sale1 = self._confirm_sale_order(carrier_id=self.delivery_carrier.id)
        sale2 = self._confirm_sale_order(carrier_id=self.delivery_carrier.id)

        # the SO
        sales = self.env["sale.order"].browse([sale1.id, sale2.id])
        self.assertFalse(sales.mapped("picking_ids.delivery_round_id"))

        # check the pickings
        # PICK has picking_type.groupbypartner = False  -> 1 by SO
        picks = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == 'PICK'
        )
        self.assertEqual(len(picks), 2)
        # outgoring has picking_type.groupbypartner = True -> 1 for the 2 SO
        ships = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == 'outgoing'
        )
        self.assertEqual(len(ships), 1)

        # create the delivery rounf
        delivery_round = self.env['round.instance'].create(
            {'template_id': self.delivery_template_2.id, 'date': '2017-01-01'}
        )

        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign must link all the pickings to
        # this new delivery round AND the 2 PICK pickings must be available
        picks.with_context(round_autoset=True)._job_action_assign()
        self.assertEqual(
            sales.mapped("picking_ids.delivery_round_id"), delivery_round
        )
        self.assertListEqual(picks.mapped("state"), ["assigned", "assigned"])

    def test_picking_assign_01(self):
        """
        Data:
            2 SO for :
              the same partner
              the same carrier
            The carrier is linked to a delivery template without instances
            The SO are confirmed with delivery_step pic + ship
            The outgoing picking is groupbypartner
        Test Case:
            Create a delivery round
            Assign the 1 pickings
        Expected results:
            The 2 pickings are into the round
            The 2 pickings PICK are available
            The 2 SO SHIP are into the same shipping
        """
        sale1 = self._confirm_sale_order(carrier_id=self.delivery_carrier.id)
        sale2 = self._confirm_sale_order(carrier_id=self.delivery_carrier.id)

        # the SO
        sales = self.env["sale.order"].browse([sale1.id, sale2.id])
        self.assertFalse(sales.mapped("picking_ids.delivery_round_id"))

        # check the pickings
        # PICK has picking_type.groupbypartner = False  -> 1 by SO
        picks = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == 'PICK'
        )
        self.assertEqual(len(picks), 2)
        # outgoring has picking_type.groupbypartner = True -> 1 for the 2 SO
        ships = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == 'outgoing'
        )
        self.assertEqual(len(ships), 1)

        # create the delivery rounf
        delivery_round = self.env['round.instance'].create(
            {'template_id': self.delivery_template_2.id, 'date': '2017-01-01'}
        )

        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign must link all the pickings to
        # this new delivery round AND the 2 PICK pickings must be available
        picks[0].with_context(round_autoset=True)._job_action_assign()
        self.assertEqual(
            sales.mapped("picking_ids.delivery_round_id"), delivery_round
        )
        self.assertListEqual(picks.mapped("state"), ["assigned", "assigned"])
