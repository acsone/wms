# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import TransactionCase


class ProductCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.variant = cls.env.ref(
            "shopinvader_product.product_product_chair_vortex_white"
        )

    def test_product_shopinvader_categories(self):
        self.assertEqual(len(self.variant.shopinvader_categ_ids), 0)
        self.variant.categ_ids = self.env.ref("alc_product_shop_category.master")
        self.assertEqual(len(self.variant.shopinvader_categ_ids), 1)
