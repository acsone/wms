# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_price_cache.tests.common import TestPrices
from odoo.addons.alc_supplier_promotion.tests.common import TestSupplierInfo


class TestPricing(TestSupplierInfo, TestPrices):
    @classmethod
    def setUpClass(cls):
        super(TestPricing, cls).setUpClass()

        # base pricelist with nothing, to make sure we get standard price
        vals_pricelist_base = cls._get_pricelist_vals("PLbase", [], is_discount=False)
        cls.pricelist_base = cls.model_pl_nodelay.create(vals_pricelist_base)

        # exclusive discount on product 1, discount on product 2, nothing on 3
        items_1 = [
            cls._get_item_vals(
                applied_on="0_product_variant",
                product_id=cls.product_1.id,
                exclusive=True,
            ),
            cls._get_item_vals(
                applied_on="0_product_variant", product_id=cls.product_2.id
            ),
        ]
        vals_pl1 = cls._get_pricelist_vals("PL1", items_1, is_discount=True)
        cls.discount_pricelist_1 = cls.model_pl_nodelay.create(vals_pl1)

        # discount on product 1, exclusive discount on product 2, nothing on 3
        items_2 = [
            cls._get_item_vals(
                applied_on="0_product_variant", product_id=cls.product_1.id,
            ),
            cls._get_item_vals(
                applied_on="0_product_variant",
                product_id=cls.product_2.id,
                exclusive=True,
            ),
        ]
        vals_pl2 = cls._get_pricelist_vals("PL2", items_2, is_discount=True)
        cls.discount_pricelist_2 = cls.model_pl_nodelay.create(vals_pl2)

        vals_sinfo_1 = cls.get_supplierinfo_vals(cls.product_1, discount_sale=20)
        vals_sinfo_1.pop("price")
        cls.supplier_info_1 = cls.supplierinfo_model.create(vals_sinfo_1)

        vals_sinfo_2 = cls.get_supplierinfo_vals(cls.product_2, discount_sale=20)
        vals_sinfo_2.pop("price")
        cls.supplier_info_2 = cls.supplierinfo_model.create(vals_sinfo_2)

        vals_product_3 = {"name": "P1", "categ_id": cls.cat_1.id, "list_price": 30}
        cls.product_3 = cls.env["product.product"].create(vals_product_3)

        vals_customer_1 = {
            "name": "C1",
            "discount_pricelist_id": cls.discount_pricelist_1.id,
            "supplier_promotion_sale_allowed": True,
        }
        cls.customer_1 = cls.env["res.partner"].create(vals_customer_1)
        cls.customer_1.property_product_pricelist = cls.pricelist_base

        cls.so_1 = cls.env["sale.order"].create({"partner_id": cls.customer_1.id})

        vals_customer_2 = {
            "name": "C2",
            "discount_pricelist_id": cls.discount_pricelist_2.id,
            "supplier_promotion_sale_allowed": True,
        }
        cls.customer_2 = cls.env["res.partner"].create(vals_customer_2)
        cls.customer_2.property_product_pricelist = cls.pricelist_base

        cls.so_2 = cls.env["sale.order"].create({"partner_id": cls.customer_2.id})

        cls.model_line = cls.env["sale.order.line"]

    @classmethod
    def _new_sale_line(cls, so, product, qty=1, **kwargs):
        base = {"product_id": product.id, "product_uom_qty": qty, "order_id": so.id}
        vals = dict(base, **kwargs)
        vals_onchange = cls.model_line.play_onchanges(vals)
        return cls.model_line.create(dict(vals, **vals_onchange))
