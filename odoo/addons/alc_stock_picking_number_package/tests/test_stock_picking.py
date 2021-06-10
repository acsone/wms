# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, round_autoset=False)
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777878"}
        )

        cls.delivery_template = cls.env["round.template"].create(
            {"name": "Unittest delivery template"}
        )
        cls.delivery_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Unittest delivery carrier",
                "delivery_type": "fixed",
                "fixed_price": 10.0,
                "delivery_template_id": cls.delivery_template.id,
                "maximum_weight_per_package": 37,
            }
        )

        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "BWH",
            }
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0001",
                "default_code": "12341",
            }
        )
        cls.product_template1 = cls.product1.product_tmpl_id
        cls.product_template1.weight = 25

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0002",
                "default_code": "12342",
            }
        )
        cls.product_template2 = cls.product2.product_tmpl_id
        cls.product_template2.weight = 30

        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0003",
                "default_code": "12343",
            }
        )
        cls.product_template3 = cls.product3.product_tmpl_id
        cls.product_template3.weight = 30

        cls.product4 = cls.env["product.product"].create(
            {
                "name": "Product 4",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0004",
                "default_code": "12344",
            }
        )
        cls.product_template4 = cls.product4.product_tmpl_id
        cls.product_template4.weight = 0.3

        cls.product5 = cls.env["product.product"].create(
            {
                "name": "Product 5",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0005",
                "default_code": "12345",
            }
        )
        cls.product_template5 = cls.product5.product_tmpl_id
        cls.product_template5.weight = 3

        cls.product6 = cls.env["product.product"].create(
            {
                "name": "Product 6",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0006",
                "default_code": "12346",
            }
        )
        cls.product_template6 = cls.product6.product_tmpl_id
        cls.product_template6.weight = 8

        cls.product7 = cls.env["product.product"].create(
            {
                "name": "Product 7",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0007",
                "default_code": "12347",
            }
        )
        cls.product_template7 = cls.product7.product_tmpl_id
        cls.product_template7.weight = 0.6

        cls.product8 = cls.env["product.product"].create(
            {
                "name": "Product 8",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0008",
                "default_code": "12348",
            }
        )
        cls.product_template8 = cls.product8.product_tmpl_id
        cls.product_template8.weight = 2

        cls.product9 = cls.env["product.product"].create(
            {
                "name": "Product 9",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0009",
                "default_code": "12349",
            }
        )
        cls.product_template9 = cls.product9.product_tmpl_id
        cls.product_template9.weight = 12

        cls.products = [
            cls.product1,
            cls.product2,
            cls.product3,
            cls.product4,
            cls.product5,
            cls.product6,
            cls.product7,
            cls.product8,
            cls.product9,
        ]
        cls.so = cls._confirm_sale_order(
            partner=cls.partner, products=cls.products, carrier=cls.delivery_carrier
        )

    @classmethod
    def _confirm_sale_order(cls, partner=None, products=None, qty=10, carrier=None):
        if partner is None:
            partner = cls.partner
        if products is None:
            products = [cls.product1]
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
            for p in products
        ]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": lines,
        }
        if carrier:
            so_values["carrier_id"] = carrier.id

        so = Sale.create(so_values)
        so.action_confirm()
        return so

    def test_00(self):
        """
        Data:
            All the products are in the SO, some are heavy, others light
        Test case:
            Check the number of packages in the shipping. Each box should not exceed 37 kg
        Expected result:
            4 packages
        """
        ship = self.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        ship._compute_theoritical_number_of_packages()
        self.assertEqual(ship.theoritical_number_of_packages, 4)

    def test_01(self):
        """
        Data:
            Only light products are considered here
        Test case:
            Check the number of packages in the shipping. Each box should not exceed 37 kg
        Expected result:
            1 package is enough
        """

        products = [
            self.product4,
            self.product5,
            self.product6,
            self.product7,
            self.product8,
            self.product9,
        ]
        lines = [
            (
                0,
                0,
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": 10,
                    "product_uom": p.uom_id.id,
                    "price_unit": 1,
                },
            )
            for p in products
        ]
        so_values = {
            "partner_id": self.partner.id,
            "warehouse_id": self.warehouse_1.id,
            "carrier_id": self.delivery_carrier.id,
            "order_line": lines,
        }

        new_so = self.env["sale.order"].create(so_values)
        new_so.action_confirm()
        ship = new_so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        ship._compute_theoritical_number_of_packages()
        self.assertEqual(ship.theoritical_number_of_packages, 1)

    def test_02(self):
        """
        Data:
            Only heavy products are considered here
        Test case:
            Check the number of packages in the shipping. Each box should not exceed 37 kg
        Expected result:
            3 packages are needed, one by product
        """
        products = [self.product1, self.product2, self.product3]
        lines = [
            (
                0,
                0,
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": 10,
                    "product_uom": p.uom_id.id,
                    "price_unit": 1,
                },
            )
            for p in products
        ]
        so_values = {
            "partner_id": self.partner.id,
            "warehouse_id": self.warehouse_1.id,
            "carrier_id": self.delivery_carrier.id,
            "order_line": lines,
        }

        new_so = self.env["sale.order"].create(so_values)
        new_so.action_confirm()
        ship = new_so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        ship._compute_theoritical_number_of_packages()
        self.assertEqual(ship.theoritical_number_of_packages, 3)
