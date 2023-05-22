# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestProductStockState(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_by_product = cls.env.ref(
            "product_stock_state.product_setting_by_product"
        )

    def test_state_supplier_out_of_stock(self):
        """Test Stock State computation."""
        self.assertEqual(self.product_by_product.stock_state, "out_of_stock")
        self.product_by_product.product_state_id = self.env.ref(
            "alc_product_state.product_state_h"
        )
        self.assertEqual(self.product_by_product.stock_state, "supplier_out_of_stock")
        self.product_by_product.product_state_id = None
        self.assertEqual(self.product_by_product.stock_state, "out_of_stock")
