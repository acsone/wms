# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_wishlist.tests.test_wishlist import CommonWishlistCase


class WishlistCase(CommonWishlistCase):
    @classmethod
    def setUpClass(cls):
        super(WishlistCase, cls).setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend

    def test_bulk_update(self):
        prod_set = self.env["product.set"].create(
            {
                "name": "Wishlist 1",
                "typology": "wishlist",
                "shopinvader_backend_id": self.backend.id,
                "partner_id": self.partner.id,
                "set_line_ids": [
                    (5, 0, 0),
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4b").id,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(prod_set.name, "Wishlist 1")
        self.assertEqual(1, len(prod_set.set_line_ids))
        params = {
            "name": "Baz",
            "lines": [
                {
                    "product_id": self.env.ref("shopinvader.product_product_39").id,
                    "quantity": 3.0,
                },
                {
                    "product_id": self.env.ref("shopinvader.product_product_41").id,
                    "quantity": 5.0,
                },
            ],
        }
        self.wishlist_service.dispatch("bulk_update", prod_set.id, params=params)
        self.assertEqual(prod_set.name, "Baz")
        self.assertEqual(2, len(prod_set.set_line_ids))
