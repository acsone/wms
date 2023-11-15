# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas import ProductProduct


class TestProductExpiryInSchema(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ExtendableMixin.init_extendable_registry()

        @cls.addClassCleanup
        def cleanup():
            ExtendableMixin.reset_extendable_registry()

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "tracking": "lot", "type": "product"}
        )
        cls.meds_category = cls.env.ref("alc_product_category_data.product_categ_medoc")
        cls.equipment_category = cls.env.ref(
            "alc_product_category_data.product_categ_materiel"
        )
        cls.psychotropic_category = cls.env.ref(
            "alc_product_category_data.product_categ_psychotropes_25"
        )
        cls.pharmaceutical_category = cls.env.ref(
            "alc_product_category_data.product_categ_parapharmacie"
        )
        cls.import_category = cls.env.ref(
            "alc_product_category_data.product_categ_importation"
        )
        cls.narcotic_vet_category = cls.env.ref(
            "alc_product_category_data.product_categ_stupefiant_vet"
        )
        cls.human_category = cls.env.ref(
            "alc_product_category_data.product_categ_humain"
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_meds)
        self.product.categ_id = self.meds_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_meds)

    def test_01(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_equipment)
        self.product.categ_id = self.equipment_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_equipment)

    def test_02(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_psychotropic)
        self.product.categ_id = self.psychotropic_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_psychotropic)

    def test_03(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_pharmaceutical)
        self.product.categ_id = self.pharmaceutical_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_pharmaceutical)

    def test_04(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_import)
        self.product.categ_id = self.import_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_import)

    def test_05(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_narcotic_vet)
        self.product.categ_id = self.narcotic_vet_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_narcotic_vet)

    def test_06(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_human)
        self.product.categ_id = self.human_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_human)

    def test_07(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.belgium_only)
        self.product.belgium_only = True
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.belgium_only)

    def test_08(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.veterinary_only)
        self.product.veterinary_only = True
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.veterinary_only)

    def test_09(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.cnk_code)
        self.product.cnk_code = "cnk_code"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.cnk_code, "cnk_code")

    def test_10(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.code_cti)
        self.product.code_cti = "code_cti"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.code_cti, "code_cti")

    def test_11(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.code_amm)
        self.product.code_amm = "code_amm"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.code_amm, "code_amm")
