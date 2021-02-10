# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import GroupByPartnerCommonCase


class TestGroupByPartner(GroupByPartnerCommonCase):
    """Check grouping of moves by partner

    The module stock_groupbypartner assigns moves to an existing picking not
    yet reserved with similar partner, locations, picking type and delivery
    carrier.
    Which means that if several orders are created for the same partner and
    these various fields have the same values, they will be grouped in the same
    picking until it is shipped.

    """

    def _create_procurement_group(self, partner, customer=None):
        customer = customer or partner
        group = self.env["procurement.group"].create(
            {
                "name": "test group",
                "move_type": "direct",
                "partner_id": partner.id,
                "customer_id": customer.id,
            }
        )
        return group

    def _create_move(self, group):
        warehouse = self.warehouse_1
        move = self.env["stock.move"].create(
            {
                "name": self.p1.name,
                "group_id": group.id,
                "partner_id": group.partner_id.id,
                "product_id": self.p1.id,
                "product_uom_qty": 1,
                "product_uom": self.p1.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": warehouse.wh_output_stock_loc_id.id,
                "picking_type_id": warehouse.pick_type_id.id,
            }
        )
        return move

    def test_assign_same_picking(self):
        """Moves with similar values are grouped"""
        group = self._create_procurement_group(self.partner1)
        move1 = self._create_move(group)
        move1.assign_picking()

        move2 = self._create_move(group)
        move2.assign_picking()

        self.assertEqual(move1.picking_id, move2.picking_id)

    def test_assign_same_picking_01(self):
        """Moves with similar values are grouped
        (here we have a customer <> partner)
        """
        group = self._create_procurement_group(self.partner1, self.partner2)
        move1 = self._create_move(group)
        move1.assign_picking()

        move2 = self._create_move(group)
        move2.assign_picking()

        self.assertEqual(move1.picking_id, move2.picking_id)

    def test_assign_other_picking_type(self):
        """Moves with different picking types are not grouped"""
        group = self._create_procurement_group(self.partner1)
        move1 = self._create_move(group)
        move1.assign_picking()

        warehouse = self.env.ref("stock.warehouse0")
        picking_sequence = warehouse.in_type_id.sequence_id
        type_ali = self.env["stock.picking.type"].create(
            {
                "name": "Pick Aliments",
                "code": "internal",
                "subcode": "PICK",
                "sequence_id": picking_sequence.id,
                "groupbypartner": True,
            }
        )

        move2 = self._create_move(group)
        move2.picking_type_id = type_ali.id
        move2.assign_picking()

        self.assertNotEqual(move1.picking_id, move2.picking_id)

    def test_assign_groupby_carrier(self):
        """Moves are grouped  by delivery carriers"""
        group = self._create_procurement_group(self.partner1)
        move1 = self._create_move(group)
        move1.assign_picking()

        group2 = self._create_procurement_group(self.partner1)
        group2.carrier_id = self.carrier_fixed.id
        move2 = self._create_move(group2)
        move2.assign_picking()
        self.assertNotEqual(move1.picking_id, move2.picking_id)

        group3 = self._create_procurement_group(self.partner1)
        move3 = self._create_move(group3)
        move3.assign_picking()
        self.assertEqual(move1.picking_id, move3.picking_id)

        group4 = self._create_procurement_group(self.partner1)
        group4.carrier_id = self.carrier_fixed.id
        move4 = self._create_move(group4)
        move4.assign_picking()
        self.assertEqual(move2.picking_id, move4.picking_id)

    def test_assign_grouby_01(self):
        """ Moves are grouped by partner"""
        group = self._create_procurement_group(self.partner1)
        move1 = self._create_move(group)
        move1.assign_picking()

        group2 = self._create_procurement_group(self.partner1)
        move2 = self._create_move(group2)
        move2.assign_picking()

        self.assertEqual(move1.picking_id, move2.picking_id)

    def test_assign_grouby_02(self):
        """ Moves are grouped by partner and customer
        Test Case:
            = partners
            = customers
        """
        group = self._create_procurement_group(self.partner1, customer=self.partner2)
        move1 = self._create_move(group)
        move1.assign_picking()

        group2 = self._create_procurement_group(self.partner1, customer=self.partner2)
        move2 = self._create_move(group2)
        move2.assign_picking()

        self.assertEqual(move1.picking_id, move2.picking_id)

    def test_assign_grouby_03(self):
        """ Moves are grouped by partner and customer
        Test Case:
            = partners
            <> customers
        """
        group = self._create_procurement_group(self.partner1)
        move1 = self._create_move(group)
        move1.assign_picking()

        group2 = self._create_procurement_group(self.partner1, customer=self.partner2)
        move2 = self._create_move(group2)
        move2.assign_picking()

        self.assertNotEqual(move1.picking_id, move2.picking_id)

    def test_assign_grouby_04(self):
        """ Moves are grouped by partner and customer
        Test Case:
            <> partners
            = customers
        """
        group = self._create_procurement_group(self.partner2, customer=self.partner2)
        move1 = self._create_move(group)
        move1.assign_picking()

        group2 = self._create_procurement_group(self.partner1, customer=self.partner2)
        move2 = self._create_move(group2)
        move2.assign_picking()

        self.assertNotEqual(move1.picking_id, move2.picking_id)

    def test_assign_grouby_05(self):
        """ Moves are grouped by partner
            Create a backorder but by specifying no_new_picking=True.
            no_new_picking=True is used when we want to avoid the creation
            of a new picking by the create_backorder method if nothing has
            been processed into original picking.
            Since the backorder is in fact the original picking, the date_done
            should not be set
        """
        group = self._create_procurement_group(self.partner1)
        move1 = self._create_move(group)
        move1.assign_picking()

        group2 = self._create_procurement_group(self.partner1)
        move2 = self._create_move(group2)
        move2.assign_picking()

        self.assertEqual(move1.picking_id, move2.picking_id)

        picking = move1.picking_id
        # force reuse of the same picking as backorder since nothing is processed
        backorder = picking.with_context(no_new_picking=True)._create_backorder()
        self.assertEquals(backorder, picking)
        self.assertFalse(picking.date_done)
        # create a new backorder
        backorder = picking._create_backorder()
        self.assertNotEqual(backorder, picking)
        self.assertTrue(picking.date_done)
