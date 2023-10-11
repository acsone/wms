# Copyright 2021 ACSONE SA/NV

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        10 product in stock.

        1 lot1 in stock
        2 lot2 in stock

        create an assign a picking with 2 moves
         1 move for 2 product
         1 move for 2 product_lot
        As result we should have 2 pack operations
         1 pack op for 2 products
         1 pack op With 2 packop_lot (1 + 1)
        """
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, round_autoset=False)
        )
        cls.partner1 = cls.env["res.partner"].create({"name": "Unittest partner"})
        ProductProduct = cls.env["product.product"]
        cls.product = ProductProduct.create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "default_code": "product_without_lot",
            }
        )

        cls.product_lot = ProductProduct.create(
            {
                "name": "Unittest P lot",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "tracking": "lot",
                "default_code": "product_with_lot",
            }
        )
        StockProductionLot = cls.env["stock.lot"]
        cls.lot1 = StockProductionLot.create(
            {
                "name": "1234",
                "product_id": cls.product_lot.id,
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.lot2 = StockProductionLot.create(
            {
                "name": "5678",
                "product_id": cls.product_lot.id,
                "company_id": cls.env.user.company_id.id,
            }
        )

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls._set_product_qty(10, cls.product, cls.stock_location)
        cls._set_product_qty(1, cls.product_lot, cls.stock_location, cls.lot1)
        cls._set_product_qty(1, cls.product_lot, cls.stock_location, cls.lot2)
        picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "move",
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                    for product in [cls.product, cls.product_lot]
                ],
            }
        )
        picking = picking.with_context(test_mode=1)
        picking.action_assign()
        cls.picking = picking

    @classmethod
    def _set_product_qty(cls, qty, product, location, lot=None):
        inventory_quant = cls.env["stock.quant"].create(
            {
                "location_id": location.id,
                "product_id": product.id,
                "inventory_quantity": qty,
                "lot_id": lot.id if lot else False,
            }
        )
        inventory_quant.action_apply_inventory()

    def _lot_2_zetes_barcode(self, lot):
        # ZETES code: S-product_code-lot_name-date...
        return f"S-{lot.product_id.default_code}-{lot.name}-"

    def _lot_to_alcyon_barcode(self, lot):
        return f"#{lot.product_id.default_code}#{lot.name}#"

    def test_barcode_process_product(self):
        pack_op = self.picking.move_line_ids.filtered(
            lambda op, product=self.product: op.product_id == product
        )
        self.assertEqual(0, pack_op.qty_done)
        # scan the product 2 times
        res = self.picking.on_barcode_scanned(self.product.default_code)
        self.assertFalse(res)
        self.assertEqual(1, pack_op.qty_done)
        res = self.picking.on_barcode_scanned(self.product.default_code)
        self.assertFalse(res)
        self.assertEqual(2, pack_op.qty_done)
        # the 3th time, a warning is returned since we scanned more than one
        # product
        res = self.picking.on_barcode_scanned(self.product.default_code)
        self.assertEqual(2, pack_op.qty_done)
        self.assertIn("warning", res)

    def test_barcode_process_lot(self):
        pack_op = self.picking.move_line_ids.filtered(
            lambda op, product=self.product_lot: op.product_id == product
        )
        self.assertEqual(0, sum(pack_op.mapped("qty_done")))
        # expected 1 lot to be scanned (lot1)
        lot_1_barcode = self._lot_to_alcyon_barcode(self.lot1)
        res = self.picking.on_barcode_scanned(lot_1_barcode)
        self.assertFalse(res)
        # a quantity has well been done
        self.assertEqual(1, sum(pack_op.mapped("qty_done")))
        # and this qty_done belongs to ml with lot1
        pack_op_scanned = pack_op.filtered(lambda x: x.lot_id == self.lot1)
        self.assertEqual(1, pack_op_scanned.qty_done)
        # on the next scan of lot1 -> error
        res = self.picking.on_barcode_scanned(lot_1_barcode)
        self.assertEqual(1, sum(pack_op.mapped("qty_done")))
        self.assertIn("warning", res)

    def test_zetes_barcode_process_lot(self):
        pack_op = self.picking.move_line_ids.filtered(
            lambda op, product=self.product_lot: op.product_id == product
        )
        self.assertEqual(0, sum(pack_op.mapped("qty_done")))
        # expected 1 lot to be scanned (lot1)
        lot_1_barcode = self._lot_2_zetes_barcode(self.lot1)
        res = self.picking.on_barcode_scanned(lot_1_barcode)
        self.assertFalse(res)

    def test_barcode_process_alldone(self):
        self.assertEqual(0, sum(self.picking.move_line_ids.mapped("qty_done")))
        # scan barcode alldone
        barcode_alldone = "C#ALLDONE"
        res = self.picking.on_barcode_scanned(barcode_alldone)
        self.assertFalse(res)
        # all quantities are done
        for ml in self.picking.move_line_ids:
            self.assertEqual(ml.qty_done, ml.reserved_uom_qty)
