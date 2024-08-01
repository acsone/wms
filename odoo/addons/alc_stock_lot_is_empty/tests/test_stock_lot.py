from odoo.tests.common import TransactionCase


class TestStockLotIsEmpty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockLot = cls.env["stock.lot"]
        cls.StockQuant = cls.env["stock.quant"]
        cls.product = cls.env.ref("product.product_product_8")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.lot = cls.StockLot.create(
            {"name": "Test Lot", "product_id": cls.product.id}
        )

    def test_0(self):
        """Test that the lot is initially empty."""
        self.assertTrue(self.lot.is_empty)

    def test_1(self):
        """Create a quant linked to the lot."""
        quant = self.StockQuant.create(
            {
                "product_id": self.lot.product_id.id,
                "location_id": self.location.id,
                "quantity": 10,
                "lot_id": self.lot.id,
            }
        )
        self.assertFalse(self.lot.is_empty)
        quant.unlink()
        self.assertTrue(self.lot.is_empty)
