# Copyright 2016 Camptocamp SA
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPricelistDiscountCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist_model = cls.env["product.pricelist"]
        cls.parameter_model = cls.env["ir.config_parameter"]
        cls.env.user.company_id.tax_calculation_rounding_method = "round_globally"
        cls.parameter_model.set_param("constrain_discount_pricelist", "1")

        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Unittest tax",
                "price_include": False,
                "amount_type": "percent",
                "amount": "0",
            }
        )

        cls.category = cls.env.ref("product.product_category_5")

        cls.supplier = cls.env.ref("base.res_partner_12")

        cls.supplierinfo1 = cls.env["product.supplierinfo"].create(
            {"partner_id": cls.supplier.id, "discount_sale": 10}
        )

        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "taxes_id": [Command.set([cls.tax.id])],
                "seller_ids": [Command.set([cls.supplierinfo1.id])],
            }
        )

        cls.supplierinfo2 = cls.env["product.supplierinfo"].create(
            {"partner_id": cls.supplier.id, "discount_sale": 10}
        )

        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "categ_id": cls.category.id,
                "taxes_id": [Command.set([cls.tax.id])],
                "seller_ids": [Command.set([cls.supplierinfo2.id])],
            }
        )

        cls.main_pricelist = cls.pricelist_model.create(
            {
                "name": "Unittest Pricelist",
                "is_discount": False,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "0_product_variant",
                            "product_id": cls.p1.id,
                            "compute_price": "fixed",
                            "fixed_price": 100,
                        },
                    ),
                    Command.create(
                        {
                            "applied_on": "0_product_variant",
                            "product_id": cls.p2.id,
                            "compute_price": "fixed",
                            "fixed_price": 200,
                        },
                    ),
                ],
            }
        )

        cls.discount_pricelist_id = cls.pricelist_model.create(
            {
                "name": "Unittest Discount Pricelist",
                "is_discount": True,
                "item_ids": [
                    Command.create(
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
        cls.discount_item = cls.discount_pricelist_id.item_ids
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Unittest partner",
                "ref": "8893294",
                "property_product_pricelist": cls.main_pricelist.id,
                "supplier_promotion_sale_allowed": True,
                "discount_pricelist_ids": [Command.set(cls.discount_pricelist_id.ids)],
            }
        )

        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        },
                    ),
                    Command.create(
                        {
                            "name": cls.p2.name,
                            "product_id": cls.p2.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        },
                    ),
                ],
            }
        )
        cls.sale.onchange_partner_id_discount_pricelist()
        cls.sol_p1 = cls.sale.order_line[0]
        cls.sol_p2 = cls.sale.order_line[1]
        cls.pricelist_base = cls.pricelist_model.create(
            {"name": "Base", "is_discount": False}
        )
        cls.pricelist_discount = cls.pricelist_model.create(
            {"name": "Discount", "is_discount": True}
        )
