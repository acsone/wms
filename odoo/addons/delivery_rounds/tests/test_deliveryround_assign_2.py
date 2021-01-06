# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import common


class TestDeliveryRoundAssign2(common.DeliveryRoundTestCase):
    """Test to run at install
    """

    @classmethod
    def setUpClass(cls):
        super(TestDeliveryRoundAssign2, cls).setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.route_medoc = cls.env.ref(
            "__setup__.stock_location_route_pick_medoc", raise_if_not_found=False
        )

        cls.route_aliment = cls.env.ref(
            "__setup__.stock_location_route_pick_ali", raise_if_not_found=False
        )

        cls.location_ali = cls.env["stock.location"].create(
            {
                "name": "Aliment",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
            }
        )

        cls.location_medoc = cls.env["stock.location"].create(
            {
                "name": "Medicament",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
            }
        )
        cls.zone_ali = cls.env["stock.location"].create(
            {"name": "A", "location_id": cls.location_ali.id}
        )

        cls.zone_medoc = cls.env["stock.location"].create(
            {"name": "G", "location_id": cls.location_medoc.id}
        )

        cls.location_product_medoc = cls.env["stock.location"].create(
            {"name": "GD80B2", "location_id": cls.zone_medoc.id}
        )

        cls.location_product_alim = cls.env["stock.location"].create(
            {"name": "AD80B2", "location_id": cls.zone_ali.id}
        )

        cls.env["stock.location"]._parent_store_compute()

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
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
        cls.warehouse_1.pick_type_id.groupbypartner = True
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

        picking_sequence = cls.warehouse_1.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")

        cls.picking_type_medoc = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Médicaments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "subcode": "PICK",
                "groupbypartner": True,
                "color": 7,
                "sequence": 4,
            }
        )

        cls.picking_type_ali = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Aliments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "subcode": "PICK",
                "groupbypartner": True,
                "color": 7,
                "sequence": 4,
            }
        )

        if not cls.route_aliment:
            cls.route_aliment = cls.env["stock.location.route"].create(
                {
                    "name": "Aliments",
                    "pull_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "pull_ali",
                                "location_id": location_out.id,
                                "picking_type_id": cls.picking_type_ali.id,
                                "location_src_id": cls.location_ali.id,
                                "procure_method": "make_to_stock",
                                "action": "move",
                            },
                        )
                    ],
                }
            )

        cls.categ_ali = cls.env.ref(
            "specific_data.product_categ_ali", raise_if_not_found=False
        )
        if not cls.categ_ali:
            cls.categ_ali = cls.env["product.category"].create(
                {"name": "Alim category"}
            )
        cls.categ_ali.route_ids = [(4, cls.route_aliment.id)]
        if not cls.route_medoc:
            cls.route_medoc = cls.env["stock.location.route"].create(
                {
                    "name": "Medicament",
                    "pull_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "pull_medoc",
                                "location_id": location_out.id,
                                "picking_type_id": cls.picking_type_medoc.id,
                                "location_src_id": cls.location_medoc.id,
                                "procure_method": "make_to_stock",
                                "action": "move",
                            },
                        )
                    ],
                }
            )
        cls.categ_medoc = cls.env.ref(
            "specific_data.product_categ_medoc", raise_if_not_found=False
        )
        if not cls.categ_medoc:
            cls.categ_medoc = cls.env["product.category"].create(
                {"name": "Medeoc category"}
            )
        cls.categ_medoc.route_ids = [(4, cls.route_medoc.id)]

    @classmethod
    def _set_qty_in_loc_only(cls, product, qty, location=None):
        location = location or cls.env.ref("stock.stock_location_stock")
        inventory = cls.env["stock.inventory"].create(
            {"name": "Test", "product_id": product.id, "filter": "product"}
        )
        inventory.prepare_inventory()
        inventory.line_ids.write({"product_qty": 0})
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "product_qty": qty,
                "location_id": location.id,
            }
        )
        inventory.action_done()
        return inventory

    def test_01(self):
        """
        In this tests we chack that if a SO create a new picking and complete an
        other one, the reservation is triggered on both pickings
        """
        # add p1 into medoc
        self._set_qty_in_loc_only(self.p1, 10, self.location_product_medoc)
        self.p1.categ_id = self.categ_medoc
        self.p1.route_ids = [(6, 0, self.route_medoc.ids)]
        # add p2 into alim
        self._set_qty_in_loc_only(self.p2, 10, self.location_product_alim)
        self.p2.categ_id = self.categ_ali
        self.p2.route_ids = [(6, 0, self.route_aliment.ids)]

        # create delivery round so the SO will be assigned to this delivery round
        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )
        delivery_round.button_resetdraft()

        # create and validate a SO for p1
        # -> one pick medoc must be created and available into the delivery round
        sale1 = self._confirm_sale_order(
            partner=self.partner1, carrier_id=self.delivery_carrier.id, product=self.p1
        )
        # at this stage the pick is assigned and into the delivery
        self.assertEqual(sale1.mapped("picking_ids.delivery_round_id"), delivery_round)
        pick = sale1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(pick.picking_type_id, self.picking_type_medoc)

        # create and validate a SO for p1 and P2
        # -> P1 must be into the same pick as first sale (available)
        # -> P2  must be in its own pick of type alim and available
        sale2 = self._confirm_sale_order(
            partner=self.partner1,
            carrier_id=self.delivery_carrier.id,
            product=self.p1 | self.p2,
        )
        self.assertEqual(sale1.mapped("picking_ids.delivery_round_id"), delivery_round)
        picks = sale2.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(len(picks), 2)
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )

        self.assertEqual(pick_medoc, pick)
        self.assertEqual(pick_alim.state, "assigned")
        self.assertEqual(pick_medoc.state, "assigned")
