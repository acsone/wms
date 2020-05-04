# coding: utf-8

from odoo import tools

from .common import TestDeliveryRound


class TestDeliveryRoundRefillAndBackorders(TestDeliveryRound):
    """tests for ALCYN-2130. Numbers come from
    https://docs.google.com/spreadsheets/d/1SnC0P-PR1qFGphmm63FXE6gxu0A1mSnCeVhgNKSbT10/edit#gid=1317659789"""

    def test_case_16(self):
        """Test case 16

        Tournée existe pour le client, état "fermé" avec déjà une livraison pour ce
        client. Le pick du client n'a pas encore été effectué. Le client passe une
        nouvelle commande avec 1 pick, marchandise disponible

        -> Un nouveau pick est créé et n'est pas inséré dans la tournée
        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1)
        # picking is not in the delivery round
        self.assertFalse(so1.mapped("picking_ids.delivery_round_id"))
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        self.assertEqual(
            so1.mapped("picking_ids.delivery_round_id"), self.delivery_round_1
        )
        # create another move -> gets grouped in same picking
        so2 = self._confirm_sale_order(self.partner1, product=self.p2)
        self.assertEqual(so2.picking_ids, so1.picking_ids)
        # close round
        self.delivery_round_1.button_close()
        self.assertEqual(self.delivery_round_1.state, "close")
        # new sale order for same partner -> pickings are not merged with the
        # ones in the closed round
        so3 = self._confirm_sale_order(self.partner1)
        self.assertFalse(so3.picking_ids & so2.picking_ids)

    def test_case_17(self):
        """Test case 17

        Tournée existe pour le client, état "fermé" avec déjà une livraison
        pour ce client. Le pick du client n'a pas encore été effectué. Le
        client passe une nouvelle commande avec 1 pick, marchandise
        disponible. La tournée est cloturée.

        -> Un nouveau pick est créé et n'est pas inséré dans la tournée. Le
           pick de la tournée est mergé avec le nouveau pick.
        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        self.delivery_round_1.button_picking_start()
        # close round
        self.delivery_round_1.button_close()
        so2 = self._confirm_sale_order(self.partner1, product=self.p2)
        # pickings from both sales orders are not merged
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        # Check that we have an instance customer
        self.assertTrue(self.delivery_round_1.instance_customer_ids)
        # terminate the round
        self.delivery_round_1.instance_customer_ids.button_deliver()
        # pickings from both sales orders are now merged
        self.assertEqual(so1.picking_ids, so2.picking_ids)
        # Check that the customer instance are deleted as delivery is done
        self.assertFalse(self.delivery_round_1.instance_customer_ids)

    def test_case_21A(self):
        """Test case 21

        Picking disponible, marchandise disponible dans odoo mais pas
        physiquement. Rupture déclarée pour la quantité manquante. Un backorder
        est créé.

        -> Le backorder reste dans la tournée mais n'est pas disponible."""
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, qty=10)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        # don't close round
        # declare rupture
        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 3.0
        pack_op.with_context(round_autoset=False)._skip_operation()
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        # a backorder is created. We can't use backorder_id to find it though,
        # we need to find a move which has a destination move in the same
        # picking as the original, but is different from the one we are
        # targetting.
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation.move_lines[0].id),
                ("picking_id", "!=", preparation.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)

    def test_case_21B(self):
        """Test case 21B

        Tournée existe pour le client, état "fermé" avec picking disponible,
        marchandise partiellement disponible. Un backorder est créé.

        -> Le backorder reste dans la tournée mais n'est pas disponible."""
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, qty=10)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        self.delivery_round_1.button_picking_start()
        # close the round
        self.delivery_round_1.button_close()
        # declare rupture
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 3.0
        pack_op.with_context(round_autoset=False)._skip_operation()
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        # a backorder is created. We can't use backorder_id to find it though,
        # we need to find a move which has a destination move in the same
        # picking as the original, but is different from the one we are
        # targetting.
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation.move_lines[0].id),
                ("picking_id", "!=", preparation.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)

    def test_case_22(self):
        """Test case 22

        Tournée existe pour le client, état "ouvert", avec picking
        partiellement disponible. Un backorder est créé. Le client passe une
        nouvelle commande avec articles dans la même zone que le backorder.

        -> Le backorder est dans la tournée mais n'est pas disponible. Le
           backorder est complété avec la nouvelle commande

        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p2, qty=20)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        # process available qty
        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 10.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        # backorder is created, not available
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation.move_lines[0].id),
                ("picking_id", "!=", preparation.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)
        # new order from same customer
        so2 = self._confirm_sale_order(self.partner1, product=self.p1, qty=20)
        preparation2 = so2.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        # backorder is completed with the new order's preparation
        self.assertEqual(backorder_preparation, preparation2)

    def test_case_23(self):
        """Test case 23

        Tournée existe pour le client, état "fermé", avec picking partiellement
        disponible. Un backorder est créé. Le client passe une nouvelle
        commande avec articles dans la même zone que le backorder.

        -> Le backorder est dans la tournée mais n'est pas disponible. Le
           backorder n'est pas complété avec la nouvelle commande

        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p2, qty=20)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        # close the round
        self.delivery_round_1.button_close()
        # process available qty
        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 10.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        # backorder is created, not available
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation.move_lines[0].id),
                ("picking_id", "!=", preparation.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)
        # new order from same customer
        so2 = self._confirm_sale_order(self.partner1, product=self.p1, qty=20)
        preparation2 = so2.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        # backorder is NOT completed with the new order's preparation
        self.assertNotEqual(backorder_preparation, preparation2)
        # the new preparation is NOT in the round instance
        self.assertNotEqual(preparation2.delivery_round_id, self.delivery_round_1)

    def test_case_24(self):
        """Test case 24

        Tournée existe pour le client, état "fermé", avec picking partiellement
        disponible. Un backorder est créé. Le client passe une nouvelle
        commande avec articles dans la même zone que le backorder. La tournée
        est cloturée sans que le backorder soit traité.

        -> Le backorder est dans la tournée mais n'est pas disponible. Le
           backorder n'est pas complété avec la nouvelle commande. A la cloture
           de la tournée, le backorder est mergé avec le pick/ship de la
           nouvelle commande.

        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p2, qty=20)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        # close the round
        self.delivery_round_1.button_close()
        # process available qty
        self.delivery_round_1.button_picking_start()
        preparation1 = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation1.pack_operation_ids[0]
        pack_op.qty_done = 10.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation1.id}
        )
        wiz._process()
        # backorder is created, not available
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation1.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation1.move_lines[0].id),
                ("picking_id", "!=", preparation1.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)
        # new order from same customer
        so2 = self._confirm_sale_order(self.partner1, product=self.p1, qty=20)
        preparation2 = so2.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        # backorder is NOT completed with the new order's preparation
        self.assertNotEqual(backorder_preparation, preparation2)
        # the new preparation is NOT in the round instance
        self.assertNotEqual(preparation2.delivery_round_id, self.delivery_round_1)
        # terminate the delivery round. We use the round.instance.customer
        # button because it does not deliver in the background.
        self.delivery_round_1.instance_customer_ids.button_deliver()
        # the preparations of both SO are merged
        so1.refresh()
        so2.refresh()
        preparation1 = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
            and p.state != "done"
        )
        preparation2 = so2.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
            and p.state != "done"
        )
        self.assertEqual(preparation1, preparation2)

    def test_case_25(self):
        """Test case 25

        Tournée existe pour le client, état "fermé", avec picking partiellement
        disponible. Un backorder est créé. Un article du backorder est à
        nouveau disponible en stock pickable (via rangement, réassort ou
        correction de stock)

        -> Le backorder est dans la tournée mais n'est pas disponible. Le
           backorder est à nouveau disponible au réappro.

        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p2, qty=20)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        # close the round
        self.delivery_round_1.button_close()
        # process available qty
        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 10.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        # backorder is created, not available
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation.move_lines[0].id),
                ("picking_id", "!=", preparation.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)
        # process refill
        refill = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse_1.int_type_id.id,
                "location_id": self.loc_reserve.id,
                "location_dest_id": self.warehouse_1.lot_stock_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.p2.name,
                            "product_id": self.p2.id,
                            "product_uom_qty": 40,
                            "product_uom": self.p2.uom_id.id,
                            "location_id": self.loc_reserve.id,
                            "location_dest_id": self.warehouse_1.lot_stock_id.id,
                        },
                    )
                ],
            }
        )
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            refill.with_context(test_queue_job_no_delay=1).action_done()
        # backorder is available
        self.assertEqual(backorder_preparation.state, "assigned")

    def test_case_26A(self):
        """Test case 26

        Tournée existe pour le client, état "fermé", avec picking partiellement
        disponible. Un backorder est créé. Un article du backorder est
        disponible en réserve

        -> Le backorder est dans la tournée mais n'est pas disponible. La
           tournée indique que le backorder est en attente de réassort.

        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p2, qty=20)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        self.assertTrue(self.delivery_round_1.has_pending_reassort)
        # close the round
        self.delivery_round_1.button_close()
        self.assertTrue(self.delivery_round_1.has_pending_reassort)
        # process available qty
        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 10.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        # backorder is created, not available
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation.move_lines[0].id),
                ("picking_id", "!=", preparation.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)
        self.assertTrue(self.delivery_round_1.has_pending_reassort)

    def test_case_26B(self):
        """Test case 26B

        Tournée existe pour le client, état 'fermé', avec picking partiellement
        disponible. Un backorder est créé. Les articles du backorder ne sont
        pas disponibles en stock pickable ni en réserve

        -> Le backorder est dans la tournée mais n'est pas disponible. La
           tournée n'indique pas ce backorder comme à faire (kanban progress
           bar).

        """
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p1, qty=200)
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        self.assertFalse(self.delivery_round_1.has_pending_reassort)
        # close the round
        self.delivery_round_1.button_close()
        self.assertFalse(self.delivery_round_1.has_pending_reassort)
        # process available qty
        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 100.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        # backorder is created, not available
        backorder_move = self.env["stock.move"].search(
            [
                (
                    "move_dest_id.picking_id",
                    "=",
                    preparation.move_lines[0].move_dest_id.picking_id.id,
                ),
                ("id", "!=", preparation.move_lines[0].id),
                ("picking_id", "!=", preparation.id),
            ]
        )
        backorder_preparation = backorder_move.picking_id
        self.assertTrue(backorder_preparation)
        # the backorder is not available
        self.assertEqual(backorder_preparation.state, "confirmed")
        # the backorder is in the round instance
        self.assertEqual(backorder_preparation.delivery_round_id, self.delivery_round_1)
        # XXXX kanban progress bar

    def test_case_17B(self):
        """Test case 17B

        Tournée existe pour le client, état "fermé" avec déjà une livraison
        pour ce client. Une autre tournée existe pour le client et est dans
        l'état "ouvert". Le client passe une nouvelle commande.

        La commande est insérée dans la 2e tournée qui est ouverte.
        """
        itinerary = self.env["round.itinerary"].create(
            {
                "name": "Itinerary 17B",
                "code": "T17B",
                "sequence": 22,
                "partner_position_ids": [
                    (0, 0, {"sequence": 10, "partner_id": self.partner1.id})
                ],
            }
        )
        self.delivery_round_1.itinerary_ids = itinerary
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p1, qty=10)
        # the pickings are automatically assigned to the delivery round
        self.assertEqual(
            so1.mapped("picking_ids.delivery_round_id"), self.delivery_round_1
        )
        # close delivery round 1
        self.delivery_round_1.button_close()
        # second delivery round, open, same itinerary
        self.delivery_round_2 = self.env["round.instance"].create(
            {
                "template_id": self.delivery_template.id,
                "date": "2017-01-02",
                "itinerary_ids": [(4, itinerary.id, 0)],
            }
        )
        self.delivery_round_2.button_resetdraft()
        # create sale order
        so2 = self._confirm_sale_order(self.partner1, product=self.p1, qty=10)
        # the pickings of so2 are automatically assigned to the delivery round 2
        self.assertEqual(
            so2.mapped("picking_ids.delivery_round_id"), self.delivery_round_2
        )

    def test_case_17C(self):
        """Test case 17C

        Tournée existe pour le client, état "fermé" avec déjà une livraison
        pour ce client. Une autre tournée existe pour le client et est dans
        l'état "ouvert". La préparation du client dans la 1ère tournée n'est
        pas réalisée, la tournée est délivrée, la livraison est sortie de la
        tournée. Pour compliquer un peu, on considère que le produit p2 est un
        produit additionnel accessoire 1 offert pour un vendu.

        La livraison est insérée dans la 2e tournée qui est ouverte.

        """
        self.p1.write(
            {
                "additional_product_id": self.p2.id,
                "ratio_additional_product": 1,
                "ratio_main_product": 1,
            }
        )
        itinerary = self.env["round.itinerary"].create(
            {
                "name": "Itinerary 17C",
                "code": "T17C",
                "sequence": 22,
                "partner_position_ids": [
                    (0, 0, {"sequence": 10, "partner_id": self.partner1.id})
                ],
            }
        )
        self.delivery_round_1.itinerary_ids = itinerary
        # round is in draft and open
        self.delivery_round_1.button_resetdraft()
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p1, qty=10)
        self.assertEqual(
            so1.mapped("picking_ids.move_lines.product_id"), self.p1 | self.p2
        )
        # the pickings are automatically assigned to the delivery round
        self.assertEqual(
            so1.mapped("picking_ids.delivery_round_id"), self.delivery_round_1
        )
        # close delivery round 1
        self.delivery_round_1.button_close()
        # second delivery round, open, same itinerary
        self.delivery_round_2 = self.env["round.instance"].create(
            {
                "template_id": self.delivery_template.id,
                "date": "2017-01-02",
                "itinerary_ids": [(4, itinerary.id, 0)],
            }
        )
        self.delivery_round_2.button_resetdraft()
        # deliver round 1 without processing the pick of so1
        # Check that we have an instance customer
        self.assertTrue(self.delivery_round_1.instance_customer_ids)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.delivery_round_1.with_context(
                test_queue_job_no_delay=1
            ).button_deliver()
        # Check that the customer instance are deleted as delivery is done
        self.assertFalse(self.delivery_round_1.instance_customer_ids)
        self.delivery_round_1.button_done()
        # the pickings of so2 are automatically assigned to the delivery round 2
        self.assertEqual(
            so1.mapped("picking_ids.delivery_round_id"), self.delivery_round_2
        )
