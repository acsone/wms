# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA//NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestComparator(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestComparator, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Arthur Flow 1", "ref": "12344566777878"}
        )
        cls.partner2 = cls.env["res.partner"].create(
            {"name": "Bernard Dupont 2", "ref": "12344566777879"}
        )
        cls.partner3 = cls.env["res.partner"].create(
            {"name": "Pol Marcus 3", "ref": "12344566777874"}
        )
        cls.partner4 = cls.env["res.partner"].create(
            {"name": "John Doe 4", "ref": "12344566777444", "is_b2c_customer": True}
        )
        cls.partner5 = cls.env["res.partner"].create(
            {"name": "Daryl Smith 5", "ref": "12344566777555", "is_b2c_customer": True}
        )
        cls.partner6 = cls.env["res.partner"].create(
            {
                "name": "Veronique Marchal 6",
                "ref": "12344566777666",
                "is_b2c_customer": True,
            }
        )
        cls.partner7 = cls.env["res.partner"].create(
            {"name": "Xavier Antoine 7", "ref": "12344566777777"}
        )
        cls.partner8 = cls.env["res.partner"].create(
            {"name": "Helene Bourreau 8", "ref": "12344566777888"}
        )
        cls.partner9 = cls.env["res.partner"].create(
            {
                "name": "Jeanne Review 9",
                "ref": "12344566777999",
                "is_b2c_customer": True,
            }
        )

        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )

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
        cls.warehouse_1.out_type_id.groupbypartner = False

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

        cls.delivery_template = cls.env["round.template"].create(
            {"name": "Unittest delivery template"}
        )

        cls.delivery_round_1 = cls.env["round.instance"].create(
            {"template_id": cls.delivery_template.id, "date": "2017-01-01"}
        )

    @classmethod
    def _create_picking_pick(cls, customer=None, partner=None):
        if not partner:
            partner = cls.partner1
        if not customer:
            customer = partner
        warehouse = cls.warehouse_1
        Picking = cls.env["stock.picking"]
        picking_values = {
            "partner_id": partner.id,
            "customer_id": customer.id,
            "picking_type_id": warehouse.pick_type_id.id,
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "location_dest_id": warehouse.wh_output_stock_loc_id.id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": cls.p1.name,
                        "product_id": cls.p1.id,
                        "picking_type_id": warehouse.pick_type_id.id,
                        "product_uom_qty": 1,
                        "product_uom": cls.p1.uom_id.id,
                        "location_id": cls.env.ref("stock.stock_location_stock").id,
                        "location_dest_id": warehouse.wh_output_stock_loc_id.id,
                    },
                )
            ],
        }
        return Picking.create(picking_values)

    @classmethod
    def _create_picking_out(cls, customer=None, partner=None):
        if not partner:
            partner = cls.partner1
        if not customer:
            customer = partner
        warehouse = cls.warehouse_1
        Picking = cls.env["stock.picking"]
        picking_values = {
            "partner_id": partner.id,
            "customer_id": customer.id,
            "picking_type_id": warehouse.out_type_id.id,
            "location_id": warehouse.wh_output_stock_loc_id.id,
            "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": cls.p1.name,
                        "product_id": cls.p1.id,
                        "picking_type_id": warehouse.out_type_id.id,
                        "product_uom_qty": 1,
                        "product_uom": cls.p1.uom_id.id,
                        "location_id": warehouse.wh_output_stock_loc_id.id,
                        "location_dest_id": cls.env.ref(
                            "stock.stock_location_customers"
                        ).id,
                    },
                )
            ],
        }
        return Picking.create(picking_values)

    def test_00(self):
        """
        Data: 8 shippings done
        Test case: We want to check that the printing of the BL for partner will be done by rank/veterinary/b2c customers
        Expected:
        - First, Shippings are sorted by rank
        - Then, Shippings are sorted by alphabetical order
        - Finally, if we have b2c customers they follow their veterinary, also by alphabetical order
        """

        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )
        # makes all the pickings done into the for the round...
        pick1 = self._create_picking_pick(partner=self.partner1)
        pick2 = self._create_picking_pick(partner=self.partner1, customer=self.partner4)
        pick3 = self._create_picking_pick(partner=self.partner1, customer=self.partner5)
        pick4 = self._create_picking_pick(partner=self.partner2)
        pick5 = self._create_picking_pick(partner=self.partner3, customer=self.partner6)
        pick6 = self._create_picking_pick(partner=self.partner3, customer=self.partner9)
        pick7 = self._create_picking_pick(partner=self.partner7)
        pick8 = self._create_picking_pick(partner=self.partner8)

        ship1 = self._create_picking_out(partner=self.partner1)
        ship2 = self._create_picking_out(partner=self.partner1, customer=self.partner4)
        ship3 = self._create_picking_out(partner=self.partner1, customer=self.partner5)
        ship4 = self._create_picking_out(partner=self.partner2)
        ship5 = self._create_picking_out(partner=self.partner3, customer=self.partner6)
        ship6 = self._create_picking_out(partner=self.partner3, customer=self.partner9)
        ship7 = self._create_picking_out(partner=self.partner7)
        ship8 = self._create_picking_out(partner=self.partner8)

        # we don't care about the details if it is really
        # in that state, we force the state to assigned to be sure that
        # these pickings will be linked to the delivery round
        pick1.move_lines.write({"state": "assigned"})
        pick2.move_lines.write({"state": "assigned"})
        pick3.move_lines.write({"state": "assigned"})
        pick4.move_lines.write({"state": "assigned"})
        pick5.move_lines.write({"state": "assigned"})
        pick6.move_lines.write({"state": "assigned"})
        pick7.move_lines.write({"state": "assigned"})
        pick8.move_lines.write({"state": "assigned"})

        ship1.move_lines.write({"state": "assigned"})
        ship2.move_lines.write({"state": "assigned"})
        ship3.move_lines.write({"state": "assigned"})
        ship4.move_lines.write({"state": "assigned"})
        ship5.move_lines.write({"state": "assigned"})
        ship6.move_lines.write({"state": "assigned"})
        ship7.move_lines.write({"state": "assigned"})
        ship8.move_lines.write({"state": "assigned"})

        pickings = (
            pick1
            | pick2
            | pick3
            | pick4
            | pick5
            | pick6
            | pick7
            | pick8
            | ship1
            | ship2
            | ship3
            | ship4
            | ship5
            | ship6
            | ship7
            | ship8
        )
        delivery_round._assign_pickings(pickings)

        # we don't care about the details if it is really
        # in that state, it is only for the round to think it is

        pick1.move_lines.write({"state": "done"})
        pick2.move_lines.write({"state": "done"})
        pick3.move_lines.write({"state": "done"})
        pick4.move_lines.write({"state": "done"})
        pick5.move_lines.write({"state": "done"})
        pick6.move_lines.write({"state": "done"})
        pick7.move_lines.write({"state": "done"})
        pick8.move_lines.write({"state": "done"})

        ship1.move_lines.write({"state": "done"})
        ship2.move_lines.write({"state": "done"})
        ship3.move_lines.write({"state": "done"})
        ship4.move_lines.write({"state": "done"})
        ship5.move_lines.write({"state": "done"})
        ship6.move_lines.write({"state": "done"})
        ship7.move_lines.write({"state": "done"})
        ship8.move_lines.write({"state": "done"})

        ship1.write({"rank": 65000})
        ship2.write({"rank": 65000})
        ship3.write({"rank": 65000})
        ship4.write({"rank": 65000})
        ship5.write({"rank": 2000})
        ship6.write({"rank": 2000})
        ship7.write({"rank": 15000})
        ship8.write({"rank": 0})

        sorted_shippings = delivery_round._get_sorted_shipping_ids()

        self.assertEqual(sorted_shippings[0].rank, 0)
        self.assertEqual(sorted_shippings[1].rank, 2000)
        self.assertEqual(sorted_shippings[2].rank, 2000)
        self.assertEqual(sorted_shippings[3].rank, 15000)
        self.assertEqual(sorted_shippings[4].rank, 65000)
        self.assertEqual(sorted_shippings[5].rank, 65000)
        self.assertEqual(sorted_shippings[6].rank, 65000)
        self.assertEqual(sorted_shippings[7].rank, 65000)

        self.assertEqual(sorted_shippings[0].customer_id.name, ship8.customer_id.name)
        self.assertEqual(sorted_shippings[1].customer_id.name, ship6.customer_id.name)
        self.assertEqual(sorted_shippings[2].customer_id.name, ship5.customer_id.name)
        self.assertEqual(sorted_shippings[3].customer_id.name, ship7.customer_id.name)
        self.assertEqual(sorted_shippings[4].customer_id.name, ship1.customer_id.name)
        self.assertEqual(sorted_shippings[5].customer_id.name, ship3.customer_id.name)
        self.assertEqual(sorted_shippings[6].customer_id.name, ship2.customer_id.name)
        self.assertEqual(sorted_shippings[7].customer_id.name, ship4.customer_id.name)

        self.assertFalse(sorted_shippings[0].customer_id.is_b2c_customer)
        self.assertTrue(sorted_shippings[1].customer_id.is_b2c_customer)
        self.assertTrue(sorted_shippings[2].customer_id.is_b2c_customer)
        self.assertFalse(sorted_shippings[3].customer_id.is_b2c_customer)
        self.assertFalse(sorted_shippings[4].customer_id.is_b2c_customer)
        self.assertTrue(sorted_shippings[5].customer_id.is_b2c_customer)
        self.assertTrue(sorted_shippings[6].customer_id.is_b2c_customer)
        self.assertFalse(sorted_shippings[7].customer_id.is_b2c_customer)
