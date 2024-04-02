# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.fields import Command, Datetime
from odoo.tests.common import TransactionCase


class TestSaleOrderLineQtyUnavailable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.location_model = cls.env["stock.location"]

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Unittest tax",
                "price_include": False,
                "amount_type": "percent",
                "amount": "0",
            }
        )

        cls.p1 = cls.env["product.template"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "4929752"}
        )

        # Create the first sale order with 10 as ordered quantity
        cls.sale_1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": Datetime.now(),
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.product_variant_ids.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 10,
                            "sequence": 1,
                        },
                    )
                ],
            }
        )

        # Create the second sale order with 5 as ordered quantity
        cls.sale_2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": Datetime.to_string(
                    Datetime.from_string(Datetime.now()) + timedelta(hours=1)
                ),
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.product_variant_ids.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 5,
                            "sequence": 1,
                        },
                    )
                ],
            }
        )

    def _define_product_qty(self, product, quantity):
        self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", self.stock_location.id),
            ]
        ).unlink()
        inventory_quant = self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "product_id": product.id,
                "inventory_quantity": quantity,
            }
        )
        inventory_quant.action_apply_inventory()

    def test_01_basic(self):
        """
        Data: 2 draft SO having each 1 line for product p1 and quantities of 10 and 5.

        case: - check quantities before SO1 confirmation
              - confirm SO1
              - confirm SO2
        result: - immediately_usable_qty = 0 for p1
                  product_qty_unavailable=10 and current_product_qty_unavailable=10
                  for SO1
                - immediately_usable_qty = -10 for p1
                  product_qty_unavailable=10 and current_product_qty_unavailable=10
                  for SO1
                  product_qty_unavailable=5 and current_product_qty_unavailable=5
                  for SO2
                - immediately_usable_qty = -15 for p1
                  product_qty_unavailable=10 and current_product_qty_unavailable=10
                  for SO1
                  product_qty_unavailable=5 and current_product_qty_unavailable=5
                  for SO2
        """
        # At test beginning, the product immediately usable quantity is 0
        self.assertEqual(self.p1.product_variant_ids[0].immediately_usable_qty, 0)

        # After the first order (qty = 10), the unavailable quantity is 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        self.assertEqual(self.sale_1.order_line[0].current_product_qty_unavailable, 10)

        # Confirm the first order

        self.sale_1.action_confirm()

        # After the confirmation of first order (qty = 10),
        # the product immediately usable quantity is -10
        self.env["product.product"].invalidate_model()
        self.env["stock.move"].invalidate_model()
        self.assertEqual(self.p1.product_variant_ids[0].immediately_usable_qty, -10)
        # After the confirmation of first order (qty = 10),
        # the unavailable quantity is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        self.assertEqual(self.sale_1.order_line[0].current_product_qty_unavailable, 10)

        # After the second order (qty = 5), the unavailable quantity is 5
        self.env["product.product"].invalidate_model()
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        self.assertEqual(self.sale_2.order_line[0].current_product_qty_unavailable, 5)

        # Confirm the second order
        self.sale_2.action_confirm()

        # After the confirmation of second order (qty = 5),
        # the product immediately usable quantity is -15
        self.assertEqual(self.p1.product_variant_ids[0].immediately_usable_qty, -15)
        # After the confirmation of second order (qty = 5),
        # the unavailable quantity on first order is already 10
        self.sale_1.invalidate_recordset()
        self.sale_2.invalidate_recordset()
        self.env["product.product"].invalidate_model()
        self.env["stock.move"].invalidate_model()
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        self.assertEqual(self.sale_1.order_line[0].current_product_qty_unavailable, 10)
        # After the confirmation of second order (qty = 5),
        # the unavailable quantity is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        self.assertEqual(self.sale_2.order_line[0].current_product_qty_unavailable, 5)

    def test_02_basic(self):
        """
        Data: 2 confirmed SO having each 1 line for product p1 and quantities of 10.

              and 5
        case: - increase the stock for product p1 by 2 units
        result: immediately_usable_qty = -13 for p1
                product_qty_unavailable=10 and current_product_qty_unavailable=8
                for SO1
                product_qty_unavailable=5 and current_product_qty_unavailable=5
                for SO2
        """
        self.sale_1.action_confirm()
        self.sale_2.action_confirm()
        self._define_product_qty(self.p1.product_variant_ids[0], 2)
        self.p1.invalidate_recordset()
        self.sale_1.invalidate_recordset()
        self.sale_2.invalidate_recordset()
        self.env["product.product"].invalidate_model()
        self.env["stock.move"].invalidate_model()

        # After the stock increase (qty = 2),
        # the product immediately usable quantity is -13
        self.assertEqual(self.p1.product_variant_ids[0].immediately_usable_qty, -13)
        # After the stock increase (qty = 2),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 8
        self.sale_1.order_line.invalidate_recordset()
        self.assertEqual(self.sale_1.order_line[0].current_product_qty_unavailable, 8)
        # After the stock increase (qty = 2),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].current_product_qty_unavailable, 5)

    def test_03_basic(self):
        """
        Data: 2 confirmed SO having each 1 line for product p1 and quantities of 10.

              and 5
        case: - increase the stock for product p1 by 11 units
        result: immediately_usable_qty = -4 for p1
                product_qty_unavailable=10 and current_product_qty_unavailable=0
                for SO1
                product_qty_unavailable=5 and current_product_qty_unavailable=4
                for SO2
        """
        self.sale_1.action_confirm()
        self.sale_2.action_confirm()
        self._define_product_qty(self.p1.product_variant_ids[0], 11)
        self.p1.invalidate_recordset()

        # After the stock increase (qty = 11),
        # the product immediately usable quantity is -4
        self.assertEqual(self.p1.product_variant_ids[0].immediately_usable_qty, -4)
        # After the stock increase (qty = 11),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 0
        self.assertEqual(self.sale_1.order_line[0].current_product_qty_unavailable, 0)
        # After the stock increase (qty = 11),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is now 4
        self.assertEqual(self.sale_2.order_line[0].current_product_qty_unavailable, 4)

    def test_04_basic(self):
        """
        Data: 2 confirmed SO having each 1 line for product p1 and quantities of 10.

              and 5
        case: - increase the stock for product p1 by 15 units
        result: immediately_usable_qty = 0 for p1
                product_qty_unavailable=10 and current_product_qty_unavailable=0
                for SO1
                product_qty_unavailable=5 and current_product_qty_unavailable=0
                for SO2
        """
        self.sale_1.action_confirm()
        self.sale_2.action_confirm()
        self._define_product_qty(self.p1.product_variant_ids[0], 15)
        self.p1.invalidate_recordset()

        # After the stock increase (qty = 15),
        # the product immediately usable quantity is 0
        self.assertEqual(self.p1.product_variant_ids[0].immediately_usable_qty, 0)
        # After the stock increase (qty = 15),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 0
        self.assertEqual(self.sale_1.order_line[0].current_product_qty_unavailable, 0)
        # After the stock increase (qty = 11),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is now 0
        self.assertEqual(self.sale_2.order_line[0].current_product_qty_unavailable, 0)

    def test_05_basic(self):
        """
        Data: 2 confirmed SO having each 1 line for product p1 and quantities of 10.

              and 5
        case: - increase the stock for product p1 by 20 units
        result: immediately_usable_qty = 5 for p1
                product_qty_unavailable=10 and current_product_qty_unavailable=0
                for SO1
                product_qty_unavailable=5 and current_product_qty_unavailable=0
                for SO2
                product_qty_unavailable=0 for SO1
        """
        self.sale_1.action_confirm()
        self.sale_2.action_confirm()
        self._define_product_qty(self.p1.product_variant_ids[0], 20)
        self.p1.invalidate_recordset()

        # After the stock increase (qty = 15),
        # the product immediately usable quantity is 5
        self.assertEqual(self.p1.product_variant_ids[0].immediately_usable_qty, 5)
        # After the stock increase (qty = 15),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 0
        self.assertEqual(self.sale_1.order_line[0].current_product_qty_unavailable, 0)
        # After the stock increase (qty = 11),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is now 0
        self.assertEqual(self.sale_2.order_line[0].current_product_qty_unavailable, 0)

        # *******************************************
        # ***** refresh_product_qties_unavailable *****
        # *******************************************
        res = self.sale_1.refresh_product_qties_unavailable()
        self.assertDictEqual({self.sale_1.order_line[0].id: -10.0}, res)
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 0)

    def test_06(self):
        """Make sure product_qty_unavailable is correctly set at order copy."""
        self.sale_1.action_confirm()
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        self._define_product_qty(self.p1.product_variant_ids[0], 100)
        # the product is now available
        sale_copy = self.sale_1.copy({})
        self.assertEqual(sale_copy.order_line[0].product_qty_unavailable, 0)
        self._define_product_qty(self.p1.product_variant_ids[0], 0)
        # the product is now unavailable
        sale_copy = self.sale_1.copy({})
        self.assertEqual(sale_copy.order_line[0].product_qty_unavailable, 10)
        sale_copy = self.sale_1.copy({})
        self.assertEqual(sale_copy.order_line[0].product_qty_unavailable, 10)
