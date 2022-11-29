# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase


class DeliveryRoundTestCase(SavepointCase):
    @contextmanager
    def mock_with_delay(self):
        with mock.patch(
            "odoo.addons.queue_job.models.base.DelayableRecordset",
            name="DelayableRecordset",
            spec=True,
        ) as delayable_cls:
            # prepare the mocks
            delayable = mock.MagicMock(name="DelayableBinding")
            delayable_cls.return_value = delayable
            yield delayable_cls, delayable

    @classmethod
    def setUpClass(cls):
        super(DeliveryRoundTestCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777878"}
        )
        cls.partner2 = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777879"}
        )
        cls.partner3 = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777874"}
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

        cls.delivery_template = cls.env["round.template"].create(
            {"name": "Unittest delivery template"}
        )

        cls.delivery_round_1 = cls.env["round.instance"].create(
            {"template_id": cls.delivery_template.id, "date": "2017-01-01"}
        )

        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "BWH",
            }
        )
        cls.warehouse_1.pick_type_id.subcode = "PICK"
        inventory = cls.env["stock.inventory"].create(
            {"name": "Test", "product_id": cls.p1.id, "filter": "product"}
        )
        inventory.prepare_inventory()
        assert not inventory.line_ids, "Inventory line should not created."
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p1.id,
                "product_uom_id": cls.env.ref("product.product_uom_unit").id,
                "product_qty": 100,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p1.id,
                "product_uom_id": cls.env.ref("product.product_uom_unit").id,
                "product_qty": 100,
                "location_id": cls.warehouse_1.wh_output_stock_loc_id.id,
            }
        )
        inventory.action_done()

    @classmethod
    def _create_picking_pick(cls, partner=None):
        if not partner:
            partner = cls.partner1
        warehouse = cls.warehouse_1
        Picking = cls.env["stock.picking"]
        picking_values = {
            "partner_id": partner.id,
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
    def _create_picking_out(cls, partner=None, picking_pick=None):
        if not partner:
            partner = cls.partner1
        warehouse = cls.warehouse_1
        Picking = cls.env["stock.picking"]
        picking_values = {
            "partner_id": partner.id,
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
        picking = Picking.create(picking_values)
        if picking_pick:
            picking_pick.move_lines.move_dest_id = picking.move_lines
        return picking

    @classmethod
    def _add_picking_pick_to_picking_out(cls, picking_pick, picking_out):
        picking_out.move_lines.product_uom_qty += (
            picking_pick.move_lines.product_uom_qty
        )
        picking_out.move_lines.move_orig_ids |= picking_pick.move_lines
        picking_pick.move_lines.move_dest_id = picking_out.move_lines

    @classmethod
    def _create_picking_pick_ship(cls, partner=None):
        pick = cls._create_picking_pick(partner=partner)
        ship = cls._create_picking_out(partner=partner, picking_pick=pick)
        return pick, ship

    @classmethod
    def _confirm_sale_order(
        cls,
        partner=None,
        product=None,
        qty=1,
        carrier_id=None,
        picking_policy=None,
        so_values=None,
    ):
        if partner is None:
            partner = cls.partner1
        if product is None:
            product = cls.p1
        warehouse = cls.warehouse_1
        Sale = cls.env["sale.order"]
        lines = [
            (
                0,
                0,
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": qty,
                    "product_uom": p.uom_id.id,
                    "price_unit": 1,
                },
            )
            for p in product
        ]
        so_values = so_values or {}
        so_values.update(
            {
                "partner_id": partner.id,
                "warehouse_id": warehouse.id,
                "order_line": lines,
            }
        )
        if picking_policy:
            so_values["picking_policy"] = picking_policy
        if carrier_id:
            so_values["carrier_id"] = carrier_id
        so = Sale.create(so_values)
        so.action_confirm()
        return so


class DeliverDeliveryRoundTestCase(DeliveryRoundTestCase):
    @classmethod
    def setUpClass(cls):
        super(DeliverDeliveryRoundTestCase, cls).setUpClass()
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
