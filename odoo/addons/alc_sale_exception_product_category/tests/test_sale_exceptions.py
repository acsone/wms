# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.addons.alc_sale_exception_settings.tests.common import (
    TestSaleOrderExceptionCommon,
)


class TestSaleOrderException(TestSaleOrderExceptionCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_module = "alc_sale_exception_product_category"
        cls.current_exception_ids = cls.get_module_exception_ids()
        cls.activate_module_exceptions_only()

        cls.prod1.categ_id = cls.env.ref(
            "alc_product_category_data.product_categ_materiel"
        )
        cls.prod_food = cls.env["product.product"].create(
            {
                "name": "I am some food, yam",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_ali_divers"
                ).id,
            }
        )
        cls.prod_stup = cls.env["product.product"].create(
            {
                "name": "I am a stupefiant",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_stupefiant"
                ).id,
            }
        )
        cls.prod_matos = cls.env["product.product"].create(
            {
                "name": "I am some gear",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_mat_instrumentation"
                ).id,
            }
        )
        cls.prod_medoc_pharma = cls.env["product.product"].create(
            {
                "name": "I am  a medoc pharmacy",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_parapharmacie"
                ).id,
            }
        )
        cls.prod_medoc_human = cls.env["product.product"].create(
            {
                "name": "I am a human medoc",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_humain"
                ).id,
            }
        )
        cls.prod_medoc_vet_belge = cls.env["product.product"].create(
            {
                "name": "I am a beligum veterinarian product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_vet_belges"
                ).id,
            }
        )
        cls.prod_medoc_belge_only = cls.env["product.product"].create(
            {
                "name": "I am a beligum medoc only",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_parapharmacie"
                ).id,
                "belgium_only": True,
            }
        )
        cls.prod_vet_only = cls.env["product.product"].create(
            {
                "name": "I am for veterinary only",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_ali_divers"
                ).id,
                "veterinary_only": True,
            }
        )
        cls.prod_psycho_III = cls.env["product.product"].create(
            {
                "name": "I am a medoc belge Psychotropes III",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_psychotropes_25"
                ).id,
            }
        )
        cls.prod_stupefiant_vet = cls.env["product.product"].create(
            {
                "name": "I am a Stupéfiant VET",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_stupefiant_vet"
                ).id,
            }
        )
        cls.prod_medoc = cls.env["product.product"].create(
            {
                "name": "Base medicine category",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_medoc"
                ).id,
            }
        )
        cls.prod_cascade_import = cls.env["product.product"].create(
            {
                "name": "I am a cascade import product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_importation"
                ).id,
            }
        )
        cls.sale_channel_phone = cls.env["sale.channel"].create(
            {
                "name": "phone",
                "code": "phone",
                "active": True,
            }
        )
        cls.sale_channel_fax = cls.env["sale.channel"].create(
            {
                "name": "fax",
                "code": "fax",
                "active": True,
            }
        )
        cls.so1_vals.update(
            {
                "sale_channel_id": cls.sale_channel_fax.id,
            }
        )
        cls.so1 = cls.env["sale.order"].create(cls.so1_vals)

    def test_customer_partner_type_misc(self):
        # self.activate_module_exceptions_only()
        self.partner.partner_type = "misc"
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        # Medoc are not allowed
        line.product_id = self.prod_medoc_pharma
        self.assertTrue(line.main_exception_id)
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.main_exception_id)
        line.product_id = self.prod_medoc_vet_belge
        self.assertTrue(line.main_exception_id)
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.main_exception_id)
        line.product_id = self.prod_vet_only
        self.assertTrue(line.main_exception_id)
        # No stup
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)

    def test_customer_partner_type_shareholder(self):
        warns = self.env["exception.rule"].search(
            [
                ("is_blocking", "=", False),
                ("id", "in", self.current_exception_ids),
            ]
        )
        warns.write({"active": 0})
        self.partner.partner_type = "shareholder"
        # Everything is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_human
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_vet_belge
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_belge_only
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_vet_only
        self.assertFalse(line.main_exception_id)
        # But not stup
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)
        warns.write({"active": 1})

    def test_customer_partner_type_veterinary(self):
        warns = self.env["exception.rule"].search(
            [
                ("is_blocking", "=", False),
                ("id", "in", self.current_exception_ids),
            ]
        )
        warns.write({"active": 0})
        self.partner.partner_type = "veterinary"
        # Everything is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_human
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_vet_belge
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_belge_only
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_vet_only
        self.assertFalse(line.main_exception_id)
        # But no stup
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)
        warns.write({"active": 1})

    def test_customer_partner_type_student_like(self):
        warns = self.env["exception.rule"].search(
            [
                ("is_blocking", "=", False),
                ("id", "in", self.current_exception_ids),
            ]
        )
        warns.write({"active": 0})
        self.partner.partner_type = "student_like"
        # Food and gear and medoc pharmacy are allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.main_exception_id)
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)
        # And vet only product should not be allowed
        line.product_id = self.prod_vet_only
        self.assertTrue(line.main_exception_id)
        warns.write({"active": 0})

    def test_customer_partner_type_wholesaler_pharmacy(self):
        # self.activate_module_exceptions_only()
        warns = self.env["exception.rule"].search(
            [
                ("is_blocking", "=", False),
                ("id", "in", self.current_exception_ids),
            ]
        )
        warns.write({"active": 0})
        self.partner.partner_type = "wholesaler_pharmacy"
        # Food and gear and medoc are allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.main_exception_id)
        # But not human medoc
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.main_exception_id)
        # And no product for vet only either
        line.product_id = self.prod_vet_only
        self.assertTrue(line.main_exception_id)
        warns.write({"active": 1})

    def test_customer_partner_type_wholesaler_veterinary(self):
        warns = self.env["exception.rule"].search(
            [
                ("is_blocking", "=", False),
                ("id", "in", self.current_exception_ids),
            ]
        )
        warns.write({"active": 0})
        self.partner.partner_type = "wholesaler_veterinary"
        # Food and gear and medoc are allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.main_exception_id)
        # And vet only product as well, for sure
        line.product_id = self.prod_vet_only
        self.assertFalse(line.main_exception_id)
        # But not human medoc
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.main_exception_id)
        warns.write({"active": 1})

    def test_customer_partner_type_export_customer(self):
        self.partner.partner_type = "export_customer"
        # Food and gear is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        # Medoc for parapharmacy are ok as well
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.main_exception_id)
        # But not other medoc
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)
        line.product_id = self.prod_medoc_vet_belge
        self.assertTrue(line.main_exception_id)
        # And not the one for belgium only
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.main_exception_id)
        # And no product for vet only either
        line.product_id = self.prod_vet_only
        self.assertTrue(line.main_exception_id)

    def test_customer_partner_type_export_meds(self):
        """Test client medicament export sale order limitations."""
        self.partner.partner_type = "export_meds"
        # Food and gear is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        # Medoc veterinary belge ok
        line.product_id = self.prod_medoc_vet_belge
        self.assertFalse(line.main_exception_id)
        # Medoc for parapharmacy are ok as well
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.main_exception_id)
        # No Psychotropes Annexe III
        line.product_id = self.prod_psycho_III
        self.assertTrue(line.main_exception_id)
        # But not other medoc
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)
        # And not the one for belgium only
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.main_exception_id)
        # And no stup
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)

    def test_customer_partner_type_equipment_only(self):
        self.partner.partner_type = "equipment_only"
        line = self.so1.order_line[0]
        # Gear is allowed
        line.product_id = self.prod_matos
        self.assertFalse(line.main_exception_id)
        # Food is not allowed
        line.product_id = self.prod_food
        self.assertTrue(line.main_exception_id)
        # No medicine allowed
        line.product_id = self.prod_medoc
        self.assertTrue(line.main_exception_id)
        # Medoc veterinary belge ok
        line.product_id = self.prod_medoc_vet_belge
        self.assertTrue(line.main_exception_id)
        # Medoc for parapharmacy are ok as well
        line.product_id = self.prod_medoc_pharma
        self.assertTrue(line.main_exception_id)
        # No Psychotropes Annexe III
        line.product_id = self.prod_psycho_III
        self.assertTrue(line.main_exception_id)
        # But not other medoc
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)
        # And not the one for belgium only
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.main_exception_id)
        # And no stup
        line.product_id = self.prod_stup
        self.assertTrue(line.main_exception_id)

    def test_exception_warning_psychotropic_product(self):
        """Check sale order line message for psychotropic products."""
        exception = self.env.ref(
            "alc_sale_exception_product_category.warning_psychotropic"
        )
        line = self.so1.order_line[0]
        line.product_id = self.prod_psycho_III
        self.assertTrue(exception.description in line.warning_text)

    def test_exception_warning_stupefiant_vet_product(self):
        """Check sale order line message for psychotropic products."""
        exception = self.env.ref(
            "alc_sale_exception_product_category.warning_stupefiant_vet"
        )
        line = self.so1.order_line[0]
        line.product_id = self.prod_stupefiant_vet
        self.assertTrue(exception.description in line.warning_text)

    def test_exceptions_by_phone(self):
        """Check psychotropic are not oredered on the phone."""
        warning = self.env.ref(
            "alc_sale_exception_product_category.warning_psychotropic"
        )
        psycotropic = self.env.ref(
            "alc_sale_exception_product_category.no_psychotropic_by_phone"
        )
        vet = self.env.ref(
            "alc_sale_exception_product_category.no_stupefiant_vet_by_phone"
        )
        self.partner.partner_type = "wholesaler_pharmacy"
        line = self.so1.order_line[0]
        line.order_id.sale_channel_id = self.sale_channel_fax
        line.product_id = self.prod_psycho_III
        # Sale order by fax the line should only have the warning displayed
        self.assertEqual(line.main_exception_id, warning)
        # Sale order by phone should have the exception
        line.order_id.sale_channel_id = self.sale_channel_phone
        # Switch product to trigger exception checking
        line.product_id = self.prod_psycho_III
        # the main exception is the warning
        self.assertEqual(line.main_exception_id, psycotropic)
        line.product_id = self.prod_food
        self.assertFalse(line.main_exception_id)
        line.product_id = self.prod_stupefiant_vet
        self.assertEqual(line.main_exception_id, vet)

    def test_exception_warning_cascade_importation(self):
        """Check sale order line message for cascade importation products."""
        exception = self.env.ref(
            "alc_sale_exception_product_category.warning_cascade_import"
        )
        line = self.so1.order_line[0]
        line.product_id = self.prod_cascade_import
        self.assertTrue(exception.description in line.warning_text)

    def test_exception_warning_medoc_human(self):
        """Check sale order line message for human medicicine."""
        exception = self.env.ref(
            "alc_sale_exception_product_category.warning_human_medoc"
        )
        line = self.so1.order_line[0]
        line.product_id = self.prod_medoc_human
        self.assertTrue(exception.description in line.warning_text)
