# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase


class TestSaleCartRestApiInfoCase(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        partner = cls.env["res.partner"].create({"name": "FastAPI Cart Demo"})

        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_cart.shopinvader_cart_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_authenticated_partner = partner.with_user(user_with_rights)
        cls.so = cls.env["sale.order"]._create_empty_cart(partner.id)
        cls.so.order_line = [
            (
                0,
                0,
                {
                    "product_id": cls.product_1.id,
                    "product_uom_qty": 1,
                    "product_uom": cls.product_1.uom_id.id,
                    "order_id": cls.so.id,
                },
            )
        ]
        cls.so = cls.so.with_user(user_with_rights)
