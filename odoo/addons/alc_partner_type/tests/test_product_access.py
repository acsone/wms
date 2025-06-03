# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

ALL_P_TYPES = {
    "guest",
    "misc",
    "student_like",
    "shareholder",
    "veterinary",
    "wholesaler_pharmacy",
    "veterinary_without_pharmacy",
    "wholesaler_veterinary",
    "equipment_only",
    "food_only",
    "export_customer",
    "export_meds",
    "supplier",
}


class TestProductAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )

        cls.product = cls.env["product.product"].create({"name": "test product access"})
        cls.categ_attribute_mapping = cls.env[
            "product.template"
        ]._get_category_attributes()

    def _assert_partner_types(self, ptypes):
        self.assertSetEqual(ptypes, set(self.product.allowed_partner_types_list))

    def test_access_all(self):
        # a product within category ALL is allowed to all partner types
        self._assert_partner_types(ALL_P_TYPES)

    def test_access_product_food(self):
        self.product.categ_id = self.env.ref("alc_product_food.product_categ_ali")
        self._assert_partner_types(ALL_P_TYPES - {"equipment_only", "guest"})

    def test_access_product_equiment(self):
        self.product.categ_id = self.env.ref(
            self.categ_attribute_mapping["is_equipment"]
        )
        self._assert_partner_types(ALL_P_TYPES - {"food_only"})

    def test_access_medoc(self):
        self.product.categ_id = self.env.ref(self.categ_attribute_mapping["is_meds"])
        self._assert_partner_types(
            ALL_P_TYPES - {"equipment_only", "food_only", "guest"}
        )

    def test_access_import(self):
        self.product.categ_id = self.env.ref(self.categ_attribute_mapping["is_import"])
        self._assert_partner_types(
            {
                "wholesaler_veterinary",
                "wholesaler_pharmacy",
                "veterinary_without_pharmacy",
                "veterinary",
                "supplier",
                "shareholder",
            }
        )

    def test_access_human(self):
        self.product.categ_id = self.env.ref(self.categ_attribute_mapping["is_human"])
        self._assert_partner_types({"veterinary", "supplier", "shareholder"})

    def test_access_vt_be(self):
        self.product.categ_id = self.env.ref(self.categ_attribute_mapping["is_vt_be"])
        self._assert_partner_types(
            ALL_P_TYPES
            - {
                "equipment_only",
                "export_customer",
                "student_like",
                "food_only",
                "misc",
                "guest",
            }
        )

    def test_access_narcotic_reg(self):
        self.product.categ_id = self.env.ref(
            self.categ_attribute_mapping["is_narcotic_reg"]
        )
        self._assert_partner_types(set())

    def test_access_narcotic_vet(self):
        self.product.categ_id = self.env.ref(
            self.categ_attribute_mapping["is_narcotic_vet"]
        )
        self._assert_partner_types({"veterinary"})

    def test_access_psychotropic(self):
        self.product.categ_id = self.env.ref(
            self.categ_attribute_mapping["is_psychotropic"]
        )
        self._assert_partner_types(
            {
                "wholesaler_veterinary",
                "wholesaler_pharmacy",
                "veterinary_without_pharmacy",
                "veterinary",
                "supplier",
                "shareholder",
            }
        )

    def test_access_pharmaceutical(self):
        self.product.categ_id = self.env.ref(
            self.categ_attribute_mapping["is_pharmaceutical"]
        )
        self._assert_partner_types(
            ALL_P_TYPES - {"equipment_only", "food_only", "guest"}
        )
