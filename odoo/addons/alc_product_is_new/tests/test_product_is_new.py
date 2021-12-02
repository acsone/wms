# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ProductNewCharacteristicsCommonFeatures


class TestProductIsNew(ProductNewCharacteristicsCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestProductIsNew, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        storage_type_new = cls.env.ref(
            "alc_stock_storage_type.package_st_M_M_Nouveaute"
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product new",
                "sale_ok": True,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "default_code": "678911",
            }
        )
        cls.product_template2 = cls.product2.product_tmpl_id
        cls.product_template2.product_package_storage_type_id = storage_type_new.id

    def test_00(self):
        "product is new"
        self.assertTrue(self.product_template2.is_new)

    def test_01(self):
        "product is not new"
        storage_type_etagere = self.env.ref(
            "alc_stock_storage_type.package_st_M_M_Etagere_Large_A"
        )
        self.product_template2.product_package_storage_type_id = storage_type_etagere.id
        self.assertFalse(self.product_template2.is_new)
