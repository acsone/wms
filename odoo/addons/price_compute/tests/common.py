# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class PriceComputeCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(PriceComputeCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.env.user.company_id.tax_calculation_rounding_method = "round_globally"

        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Unittest tax",
                "price_include": False,
                "amount_type": "percent",
                "amount": "0",
            }
        )

        cls.category = cls.env.ref("product.product_category_5")

        cls.p1 = cls.env["product.product"].create(
            {"name": "Unittest P1", "taxes_id": [(6, False, [cls.tax.id])]}
        )

        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "categ_id": cls.category.id,
                "taxes_id": [(6, False, [cls.tax.id])],
            }
        )

        cls.pricelist_item_product_rule = cls.env["product.pricelist"].create(
            {
                "name": "Unittest Pricelist",
                "item_ids": [
                    (
                        0,
                        False,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": cls.p1.id,
                            "compute_price": "fixed",
                            "fixed_price": 100,
                        },
                    ),
                ],
            }
        )

        cls.pricelist_item_category_rule = cls.env["product.pricelist"].create(
            {
                "name": "Unittest Discount Pricelist",
                "item_ids": [
                    (
                        0,
                        False,
                        {
                            "applied_on": "2_product_category",
                            "categ_id": cls.category.parent_id.id,
                            "compute_price": "percentage",
                            "percent_price": 5,
                        },
                    )
                ],
            }
        )
