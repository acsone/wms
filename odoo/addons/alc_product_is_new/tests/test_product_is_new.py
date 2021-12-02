# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ProductNewCharacteristicsCommonFeatures


class TestProductIsNew(ProductNewCharacteristicsCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestProductIsNew, cls).setUpClass()

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
