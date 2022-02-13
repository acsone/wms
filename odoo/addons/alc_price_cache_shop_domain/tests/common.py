# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_price_cache.tests.common import TestPrices


class TestPriceDomain(TestPrices):
    @classmethod
    def setUpClass(cls):
        super(TestPriceDomain, cls).setUpClass()

        cls.product_1.web_published = True
        cls.product_2.web_published = False

        cls.product_whitelisted = cls.product_2.copy()
        cls.product_blacklisted = cls.product_1.copy()

        cls.assortment = cls.env.ref("alc_eshop.shopinvader_assortment_store")
