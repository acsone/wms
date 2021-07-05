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

    def test_all_products(self):
        """
        Data:
            All the products are in the SO, some are heavy, others light
        Test case:
            Check the number of packages in the shipping. Each box should not exceed 37 kg
            We have a lot of products in this shipping:
            10 product1 with weight of 25kg each => 250kg
            10 product2 with weight of 30kg each => 300kg
            10 product3 with weight of 30kg each => 300kg
            10 product4 with weight of 0.3kg each => 3kg
            10 product5 with weight of 3kg each => 30kg
            10 product6 with weight of 8kg each => 80kg
            10 product7 with weight of 0.6kg each => 6kg
            10 product8 with weight of 2kg each => 20kg
            10 product9 with weight of 12kg each => 120kg

            We will have a list of weights:
            [0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,0.3,
            0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,0.6,
            2,2,2,2,2,2,2,2,2,2,
            3,3,3,3,3,3,3,3,3,3,
            8,8,8,8,8,8,8,8,8,8,
            12,12,12,12,12,12,12,12,12,12,
            25,25,25,25,25,25,25,25,25,25,
            30,30,30,30,30,30,30,30,30,30,
            30,30,30,30,30,30,30,30,30,30]


            All the 0.3kg products will go in one pack with one 30 and 6 products of 0.6kg leading to a pack of 36.6kg => 1 pack
            4 products of 0.6kg will go with another of 30 and 2 of 2 leading to a second pack of 36.4kg => 1 pack
            3 products of 2 kg will go with one of 30 leading to 36kg => 1 pack
            3 products of 2 kg will go with one of 30 leading to 36kg => 1 pack
            2 products of 2 kg will go with one of 30 and one of 3 leading to 37kg  => 1 pack
            2 products of 3 kg will go with one of 30 leading to 36kg => 1 pack
            2 products of 3 kg will go with one of 30 leading to 36kg => 1 pack
            2 products of 3 kg will go with one of 30 leading to 36kg => 1 pack
            2 products of 3 kg will go with one of 30 leading to 36kg => 1 pack
            1 products of 3 kg will go with one of 30 leading to 36kg => 1 pack
            10 packs of 30
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            1 product of 8 and 1 product of 25 leading to 32kg => 1 pack
            3 products of 12 leading to 36 kg => 1 pack
            3 products of 12 leading to 36 kg => 1 pack
            3 products of 12 leading to 36 kg => 1 pack
            1 remaining of 12 => 1 pack

        Expected result:
            34 packages
        """
        ship = self.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        ship._compute_theoritical_number_of_packages()
        self.assertEqual(ship.theoritical_number_of_packages, 34)

    def test_light_products(self):
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
                    "product_uom_qty": 1,
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

    def test_one_product(self):
        """
        Data:
            Only one product is considered here
        Test case:
            Check the number of packages in the shipping. Each box should not exceed 37 kg
        Expected result:
            1 package is enough
        """

        so_values = {
            "partner_id": self.partner.id,
            "warehouse_id": self.warehouse_1.id,
            "carrier_id": self.delivery_carrier.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product4.name,
                        "product_id": self.product4.id,
                        "product_uom_qty": 1,
                        "product_uom": self.product4.uom_id.id,
                        "price_unit": 1,
                    },
                )
            ],
        }

        new_so = self.env["sale.order"].create(so_values)
        new_so.action_confirm()
        ship = new_so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        ship._compute_theoritical_number_of_packages()
        self.assertEqual(ship.theoritical_number_of_packages, 1)

    def test_heavy_products(self):
        """
        Data:
            Only heavy products are considered here
        Test case:
            Check the number of packages in the shipping. Each box should not exceed 37 kg
        Expected result:
            30 packages are needed, one by product
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
        self.assertEqual(ship.theoritical_number_of_packages, 30)
