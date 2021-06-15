# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestStockPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, NO_GLS_SEND=True)
        )
        cls.currency_id = cls.env.user.company_id.currency_id
        cls.carrier = cls.env.ref(
            "alc_delivery_carrier_gls.delivery_carrier_gls_be", raise_if_not_found=False
        )
        delivery_template = cls.env["round.template"].create(
            {"name": "Unittest delivery template"}
        )
        if not cls.carrier:

            cls.carrier = cls.env["delivery.carrier"].create(
                {
                    "name": "Unittest delivery GLS",
                    "delivery_type": "fixed",
                    "fixed_price": 10.0,
                    "delivery_template_id": delivery_template.id,
                }
            )
            cls.env["ir.model.data"].create(
                {
                    "module": "alc_delivery_carrier_gls",
                    "name": "delivery_carrier_gls_be",
                    "model": "delivery.carrier",
                    "res_id": cls.carrier.id,
                }
            )

        cls.carrier.write(
            {
                "price_rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "price_rule",
                            "variable": "price",
                            "operator": "<=",
                            "max_value": 300,
                        },
                    )
                ]
            }
        )
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777878"}
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
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 30.0,
            }
        )

        cls.p4 = cls.env["product.product"].create(
            {
                "name": "Unittest P4",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 40.0,
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
        cls.warehouse_1.pick_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.create_invoice_on_transfer = True

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.StockPicking = cls.env["stock.picking"]

        picking_sequence = cls.warehouse_1.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")

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

        cls.categ_ali = cls.env["product.category"].create({"name": "Alim category"})
        cls.categ_ali.route_ids = [(4, cls.route_aliment.id)]

        cls.route_medoc = cls.env.ref(
            "__setup__.stock_location_route_pick_medoc", raise_if_not_found=False
        )

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
            cls.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "stock_location_route_pick_medoc",
                    "model": "stock.location.route",
                    "res_id": cls.route_medoc.id,
                }
            )

        cls.categ_medoc = cls.env["product.category"].create(
            {"name": "Medeoc category"}
        )
        cls.categ_medoc.route_ids = [(4, cls.route_medoc.id)]

        # add p1 into medoc
        cls._set_qty_in_loc_only(cls.p1, 10, cls.location_product_medoc)
        cls.p1.categ_id = cls.categ_medoc
        cls.p1.route_ids = [(6, 0, cls.route_medoc.ids)]
        # add p2 into alim
        cls._set_qty_in_loc_only(cls.p2, 10, cls.location_product_alim)
        cls.p2.categ_id = cls.categ_ali
        cls.p2.route_ids = [(6, 0, cls.route_aliment.ids)]
        # add p3 into medoc
        cls._set_qty_in_loc_only(cls.p3, 10, cls.location_product_medoc)
        cls.p3.categ_id = cls.categ_medoc
        cls.p3.route_ids = [(6, 0, cls.route_medoc.ids)]
        # add p4 into alim
        cls._set_qty_in_loc_only(cls.p4, 10, cls.location_product_alim)
        cls.p4.categ_id = cls.categ_ali
        cls.p4.route_ids = [(6, 0, cls.route_aliment.ids)]

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

    @classmethod
    def _confirm_sale_order(cls, partner=None, product=None, qty=1, carrier_id=None):
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
                    "price_unit": 10,
                },
            )
            for p in product
        ]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": lines,
        }
        if carrier_id:
            so_values["carrier_id"] = carrier_id
        so = Sale.create(so_values)
        so.action_confirm()
        return so

    def test_00(self):
        """
        Data: One SO with 2 medoc and 2 ali
        Test Case: Process the pickings then the shipping
        Expected Result: Only one pack medoc with added aliments in it
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p2, self.p3, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc.force_assign()

        for pack in pick_medoc.pack_operation_product_ids:
            pack.qty_done = pack.product_qty

        pack_medoc = pick_medoc.put_in_pack()
        pick_medoc.do_transfer()

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty
        final_pack = ship.put_in_pack()

        self.assertEqual(final_pack.id, pack_medoc.id)
        for pack in ship.pack_operation_ids:
            self.assertEqual(pack.result_package_id.id, pack_medoc.id)

    def test_01(self):
        """
        Data: One SO with 2 ali
        Test Case: Process the pickings then the shipping
        Expected Result: Everything stays as usual
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p2, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        self.assertFalse(pick_medoc)

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty
        final_pack = ship.put_in_pack()
        final_pack_id = (
            final_pack["res_id"] if isinstance(final_pack, dict) else final_pack.id
        )
        self.assertEqual(
            final_pack_id, ship.mapped("pack_operation_ids.result_package_id").id
        )

    def test_02(self):
        """
        Data: One SO with 2 medoc and 2 ali
        Test Case: Medoc are not put in pack
        Expected Result: Call super and create a new package
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p2, self.p3, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc.force_assign()

        for pack in pick_medoc.pack_operation_product_ids:
            pack.qty_done = pack.product_qty

        pick_medoc.do_transfer()

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty

        final_pack = ship.put_in_pack()
        final_pack_id = (
            final_pack["res_id"] if isinstance(final_pack, dict) else final_pack.id
        )
        self.assertEqual(
            final_pack_id, ship.mapped("pack_operation_ids.result_package_id").id
        )

    def test_03(self):
        """
        Data: 2 SO, one with 2 medoc and 2 ali. The other with 2 medoc
        Test Case: Medoc are put in pack twice, creating 2 packs
        Expected Result: Raise error for medoc because 2 packs
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p2, self.p3, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc.force_assign()

        for pack in pick_medoc.pack_operation_product_ids:
            pack.qty_done = 5
        pick_medoc.put_in_pack()
        pick_medoc.do_transfer()

        sale2 = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p3],
            carrier_id=self.carrier.id,
        )
        picks2 = sale2.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_medoc2 = picks2.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc2.force_assign()
        for pack in pick_medoc2.pack_operation_product_ids:
            pack.qty_done = pack.product_qty

        pick_medoc2.put_in_pack()
        pick_medoc2.do_transfer()

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty

        with self.assertRaises(ValidationError):
            ship.put_in_pack()
