# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_pricelist_discount.tests.common import TestPricelistDiscount


class TestConstraints(TestPricelistDiscount):
    @classmethod
    def setUpClass(cls):
        super(TestConstraints, cls).setUpClass()

        cls.product_template = cls.env["product.template"].create({"name": "P"})
        cls.product = cls.product_template.product_variant_ids[0]

    @classmethod
    def _get_item_vals(cls, pricelist=None, **kwargs):
        vals = {
            "applied_on": "3_global",
            "compute_price": "percentage",
            "percent_price": 10,
        }
        if pricelist:
            vals["pricelist_id"] = pricelist.id
        return dict(vals, **kwargs)
