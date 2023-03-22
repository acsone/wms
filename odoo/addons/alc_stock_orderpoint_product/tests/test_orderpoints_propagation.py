# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestOrderpointsPropagation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product1",
                "default_code": "987654321",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "active": True,
            }
        )
        cls.product_tmpl = cls.product.product_tmpl_id
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654312",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "active": True,
            }
        )
        cls.product_tmpl2 = cls.product2.product_tmpl_id

        cls.orderpoint1 = cls.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id,
                "product_min_qty": 1,
                "product_max_qty": 10,
                "qty_multiple": 2,
            }
        )

    def test_update_orderpoint_min_max_on_product_check_propagates_on_orderpoints(self):
        # First check that the info from the orderpoint is set on product template
        self.assertEqual(self.product_tmpl.orderpoint_min, 1)
        self.assertEqual(self.product_tmpl.orderpoint_max, 10)
        self.assertEqual(self.product_tmpl.orderpoint_qty_multiple, 2)

        # Update value on product template and check it is propagated to orderpoints
        self.product_tmpl.orderpoint_min = 3
        self.assertEqual(self.orderpoint1.product_min_qty, 3)

        self.product_tmpl.orderpoint_max = 30
        self.assertEqual(self.orderpoint1.product_max_qty, 30)

        self.product_tmpl.orderpoint_qty_multiple = 5
        self.assertEqual(self.orderpoint1.qty_multiple, 5)

    def test_update_orderpoint_min_max_check_propagates_on_product(self):
        # Update value on orderpoints and check it is propagated to product
        self.orderpoint1.product_min_qty = 3
        self.assertEqual(self.product_tmpl.orderpoint_min, 3)

        self.orderpoint1.product_max_qty = 30
        self.assertEqual(self.product_tmpl.orderpoint_max, 30)

        self.orderpoint1.qty_multiple = 5
        self.assertEqual(self.product_tmpl.orderpoint_qty_multiple, 5)

    def test_set_min_max_on_product_creates_orderpoint(self):
        self.product_tmpl2.write(
            {"orderpoint_min": 5, "orderpoint_max": 15, "orderpoint_qty_multiple": 3}
        )

        orderpoint2 = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product2.id)]
        )

        self.assertEqual(orderpoint2.product_min_qty, 5)
        self.assertEqual(orderpoint2.product_max_qty, 15)
        self.assertEqual(orderpoint2.qty_multiple, 3)

    def test_create_orderpoint_propagates_values_on_product(self):
        orderpoint2 = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.product2.id,
                "product_uom": self.product2.uom_id,
                "product_min_qty": 2,
                "product_max_qty": 120,
                "qty_multiple": 4,
            }
        )
        self.assertTrue(orderpoint2.active)
        self.assertEqual(self.product_tmpl2.orderpoint_min, 2)
        self.assertEqual(self.product_tmpl2.orderpoint_max, 120)
        self.assertEqual(self.product_tmpl2.orderpoint_qty_multiple, 4)

    def test_archive_orderpoint_set_values_to_zero_on_product(self):
        self.orderpoint1.active = False
        self.orderpoint1.flush_recordset()
        self.assertTrue(self.product.active)
        self.assertEqual(self.product_tmpl.orderpoint_min, 0)
        self.assertEqual(self.product_tmpl.orderpoint_max, 0)
        self.assertEqual(self.product_tmpl.orderpoint_qty_multiple, 0)
        location = self.env["stock.location"].create(
            {"location_id": self.orderpoint1.location_id.id, "name": "TEST"}
        )
        orderpoint2 = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.product.id,
                "product_uom": self.product.uom_id,
                "product_min_qty": 2,
                "product_max_qty": 120,
                "qty_multiple": 4,
                "location_id": location.id,
            }
        )
        self.assertTrue(orderpoint2.active)
        self.assertEqual(self.product_tmpl.orderpoint_min, 2)
        self.assertEqual(self.product_tmpl.orderpoint_max, 120)
        self.assertEqual(self.product_tmpl.orderpoint_qty_multiple, 4)
        # Once orderpoint rule is archived, we can archive the product
        orderpoint2.active = False
        self.product.active = False
        self.assertFalse(self.product.active)
