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
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.subcode = "PICK"
        cls.warehouse_1.pick_type_id.groupbypartner = False
        cls.warehouse_1.out_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.create_invoice_on_transfer = True

        # we create a template but without delivery round instante
        cls.delivery_template_2 = cls.env["round.template"].create(
            {"name": "Unittest delivery template 2"}
        )

        cls.delivery_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Unittest shipping costs",
                "delivery_type": "fixed",
                "fixed_price": 10.0,
                "delivery_template_id": cls.delivery_template_2.id,
            }
        )
        cls.delivery_round_1.state = "draft"
        cls.StockPicking = cls.env["stock.picking"]

    def _prepare_delivery_round(self):
        """
         Data:
            2 SO for :
              the same partner
              the same carrier
            The carrier is linked to a delivery template without instances
            The SO are confirmed with delivery_step pic + ship
            The outgoing picking is groupbypartner
        Process:
            Create a delivery round
            Assign the 1 pickings
        Status:
            The 2 pickings are into the round
            The 2 pickings PICK are available
            The 2 SO SHIP are into the same shipping
        return: delivery_round, picks, ships
        """
        sale1 = self._confirm_sale_order(carrier_id=self.delivery_carrier.id)
        sale2 = self._confirm_sale_order(carrier_id=self.delivery_carrier.id)
        # the SO
        sales = self.env["sale.order"].browse([sale1.id, sale2.id])
        self.assertFalse(sales.mapped("picking_ids.delivery_round_id"))

        # check the pickings
        # PICK has picking_type.groupbypartner = False  -> 1 by SO
        picks = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(len(picks), 2)
        # outgoring has picking_type.groupbypartner = True -> 1 for the 2 SO
        ships = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        self.assertEqual(len(ships), 1)

        # create the delivery rounf
        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )

        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign must link all the pickings to
        # this new delivery round AND the 2 PICK pickings must be available
        picks.with_context(round_autoset=True)._job_action_assign()
        self.assertEqual(sales.mapped("picking_ids.delivery_round_id"), delivery_round)
        self.assertListEqual(picks.mapped("state"), ["assigned", "assigned"])

        return delivery_round, picks, ships

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
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(len(picks), 2)
        # outgoring has picking_type.groupbypartner = True -> 1 for the 2 SO
        ships = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        self.assertEqual(len(ships), 1)

        # create the delivery rounf
        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )

        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign must link all the pickings to
        # this new delivery round AND the 2 PICK pickings must be available
        picks.with_context(round_autoset=True)._job_action_assign()
        self.assertEqual(sales.mapped("picking_ids.delivery_round_id"), delivery_round)
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
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(len(picks), 2)
        # outgoring has picking_type.groupbypartner = True -> 1 for the 2 SO
        ships = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        self.assertEqual(len(ships), 1)

        # create the delivery rounf
        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )

        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign must link all the pickings to
        # this new delivery round AND the 2 PICK pickings must be available
        picks[0].with_context(round_autoset=True)._job_action_assign()
        self.assertEqual(sales.mapped("picking_ids.delivery_round_id"), delivery_round)
        self.assertListEqual(picks.mapped("state"), ["assigned", "assigned"])

    def test_deliver_01(self):
        """
        Data:
            partner1 accept backorder
            A delivery_round with picks for partner1:
               * 2 pickings PICK are available
               * 2 SO SHIP are into the same shipping
        Test Case:
            Deliver the order even if no picking are done
        Expected results:
            2 Backorders must be created (one for each pick)
            backorders must be assigned
        """
        self.partner1.is_sale_back_order_cancel = False
        delivery_round, picks, ships = self._prepare_delivery_round()
        pickings = self.StockPicking.search([])
        delivery_round.button_close()
        delivery_round._deliver(background=False)
        new_pickings = self.StockPicking.search([]) - pickings
        self.assertEqual(2, len(new_pickings))
        self.assertEqual(picks, new_pickings.mapped("backorder_id"))
        self.assertListEqual(["assigned", "assigned"], new_pickings.mapped("state"))

    def test_deliver_02(self):
        """
        Data:
            partner1 refuse backorder
            A delivery_round with picks for partner1:
               * 2 pickings PICK are available
               * 2 SO SHIP are into the same shipping
        Test Case:
            Deliver the order even if no picking are done
        Expected results:
            no backoders created
        """
        self.partner1.is_sale_back_order_cancel = True
        delivery_round, picks, ships = self._prepare_delivery_round()
        pickings = self.StockPicking.search([])
        delivery_round.button_close()
        delivery_round._deliver(background=False)
        new_pickings = self.StockPicking.search([]) - pickings
        self.assertFalse(new_pickings)

    def test_picking_assign_03(self):
        """
        Tournée existe pour le client, état "ouverte" avec déjà une livraison pour ce
        client. Le pick du client a débuté avec zetes. Le client passe une
        nouvelle commande avec 1 pick, marchandise disponible
        Dans le picking commencé, on a 2 moves pour deux produits différents
        mais 1 opération car 1 des deux produits n'est pas disponibles

        -> Un nouveau pick est créé et est inséré dans la tournée
        -> L'opération du premier pick n'a pas été supprimée par la confirmation
        de la deuxième commande
        """
        # ensures that pickings out are grouped by partner
        # self.warehouse_1.pick_type_id.groupbypartner = True
        self.warehouse_1.out_type_id.groupbypartner = True
        delivery_carrier = self.env["delivery.carrier"].create(
            {
                "name": "Unittest shipping costs",
                "delivery_type": "fixed",
                "fixed_price": 10.0,
                "delivery_template_id": self.delivery_template.id,
            }
        )
        # create a new produit without stock to have one move whitout packop
        # into the first picking
        p3 = self.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": self.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(
            self.partner1, product=self.p1 | p3, carrier_id=delivery_carrier.id
        )

        # picking is in the delivery round
        self.assertEqual(
            so1.mapped("picking_ids.delivery_round_id"), self.delivery_round_1
        )
        #
        # start pick 1 and process available qty
        self.delivery_round_1.button_picking_start()
        so1_picking_pick = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        so1_picking_pick.assign_operator()
        # start the picking:
        pack_op_ids = so1_picking_pick.pack_operation_ids.ids
        self.assertEqual(1, len(pack_op_ids))
        self.assertEqual(2, len(so1_picking_pick.move_lines))

        # create another move -> gets grouped in same picking
        so2 = self._confirm_sale_order(self.partner1, carrier_id=delivery_carrier.id)
        # picking2 is in the delivery round
        self.assertEqual(
            so2.mapped("picking_ids.delivery_round_id"), self.delivery_round_1
        )
        # pick are <> but out are equals
        so2_picking_pick = so2.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        self.assertNotEqual(so2_picking_pick, so1_picking_pick)
        so1_picking_out = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.out_type_id
        )
        so2_picking_out = so2.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.out_type_id
        )
        self.assertEqual(so1_picking_out, so2_picking_out)

        # pack_op_ids into the picking are not changed
        self.assertEqual(pack_op_ids, so1_picking_pick.pack_operation_ids.ids)
