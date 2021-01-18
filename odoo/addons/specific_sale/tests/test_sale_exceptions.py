# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase


class TestSaleOrderException(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderException, cls).setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.ref = "888534954"
        cls.prod1 = cls.env.ref("product.product_product_1")
        cls.prod1.categ_id = cls.env.ref("specific_data.product_categ_materiel")
        cls.prod_food = cls.env["product.product"].create(
            {
                "name": "I am some food, yam",
                "categ_id": cls.env.ref("specific_data.product_categ_ali_divers").id,
            }
        )
        cls.prod_stup = cls.env["product.product"].create(
            {
                "name": "I am a stupefiant",
                "categ_id": cls.env.ref("specific_data.product_categ_stupefiant").id,
            }
        )
        cls.prod_matos = cls.env["product.product"].create(
            {
                "name": "I am some gear",
                "categ_id": cls.env.ref(
                    "specific_data.product_categ_mat_instrumentation"
                ).id,
            }
        )
        cls.prod_medoc_pharma = cls.env["product.product"].create(
            {
                "name": "I am  a medoc pharmacy",
                "categ_id": cls.env.ref("specific_data.product_categ_parapharmacie").id,
            }
        )
        cls.prod_medoc_human = cls.env["product.product"].create(
            {
                "name": "I am a human medoc",
                "categ_id": cls.env.ref("specific_data.product_categ_humain").id,
            }
        )
        cls.prod_medoc_vet_belge = cls.env["product.product"].create(
            {
                "name": "I am a beligum veterinarian product",
                "categ_id": cls.env.ref("specific_data.product_categ_vet_belges").id,
            }
        )
        cls.prod_medoc_belge_only = cls.env["product.product"].create(
            {
                "name": "I am a beligum medoc only",
                "categ_id": cls.env.ref("specific_data.product_categ_parapharmacie").id,
                "belgium_only": True,
            }
        )
        cls.prod_vet_only = cls.env["product.product"].create(
            {
                "name": "I am for veterinary only",
                "categ_id": cls.env.ref("specific_data.product_categ_ali_divers").id,
                "veterinary_only": True,
            }
        )
        cls.prod_psycho_III = cls.env["product.product"].create(
            {
                "name": "I am a medoc belge Psychotropes III",
                "categ_id": cls.env.ref(
                    "specific_data.product_categ_psychotropes_25"
                ).id,
            }
        )
        cls.prod_stupefiant_vet = cls.env["product.product"].create(
            {
                "name": "I am a Stupéfiant VET",
                "categ_id": cls.env.ref(
                    "specific_data.product_categ_stupefiant_vet"
                ).id,
            }
        )
        cls.prod_medoc = cls.env["product.product"].create(
            {
                "name": "Base medicine category",
                "categ_id": cls.env.ref("specific_data.product_categ_medoc").id,
            }
        )
        cls.prod_cascade_import = cls.env["product.product"].create(
            {
                "name": "I am a cascade import product",
                "categ_id": cls.env.ref("specific_data.product_categ_importation").id,
            }
        )
        cls.prod_provision_on_sale = cls.env["product.product"].create(
            {"name": "product provision on sale"}
        )
        cls.prod_provision_on_sale.route_ids = [
            (4, cls.env.ref("stock.route_warehouse0_mto").id, False)
        ]
        cls.delivery = cls.env["delivery.carrier"].search(
            [("free_if_more_than", "=", False)], limit=1
        )
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2018-01-29",
                "sale_channel": "fax",
                "carrier_id": cls.delivery.id,
                "client_order_ref": "whatever the client want",
                "delivery_price": 23.5,
                "suite_name": "0123434234",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": cls.prod1.name,
                            "product_id": cls.prod1.id,
                            "product_uom_qty": 7,
                        },
                    )
                ],
            }
        )

    def test_customer_with_unknown_category(self):
        """Check exceptions for a customer with no Alcyon Category set."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        self.partner.alcyon_category_id = None
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        # Medoc are not allowed
        line.product_id = self.prod_medoc_pharma
        self.assertTrue(line.exception)
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.exception)
        line.product_id = self.prod_medoc_vet_belge
        self.assertTrue(line.exception)
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.exception)
        line.product_id = self.prod_vet_only
        self.assertTrue(line.exception)
        # No stup
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_client_alcyonnaire(self):
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        warns = self.env["exception.rule"].search([("warning_only", "=", 1)])
        warns.write({"active": 0})
        # Need the correct category for this one ?
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_alcyonaire"
        )
        # Everything is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_human
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_vet_belge
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_belge_only
        self.assertFalse(line.exception)
        line.product_id = self.prod_vet_only
        self.assertFalse(line.exception)
        # But not stup
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_client_veterinary_with_depot(self):
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        warns = self.env["exception.rule"].search([("warning_only", "=", 1)])
        warns.write({"active": 0})
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_veterinary"
        )
        # Everything is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_human
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_vet_belge
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_belge_only
        self.assertFalse(line.exception)
        line.product_id = self.prod_vet_only
        self.assertFalse(line.exception)
        # But no stup
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_client_students(self):
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        warns = self.env["exception.rule"].search([("warning_only", "=", 1)])
        warns.write({"active": 0})
        # Test customer students
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_student"
        )
        # Food and gear and medoc pharmacy are allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.exception)
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.exception)
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        # And vet only product as well, I guess
        line.product_id = self.prod_vet_only
        self.assertFalse(line.exception)
        rules.write({"active": 0})

    def test_client_pharmacist_wholesale_human(self):
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        warns = self.env["exception.rule"].search([("warning_only", "=", 1)])
        warns.write({"active": 0})
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_pharmacy"
        )
        # Food and gear and medoc are allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.exception)
        # But not human medoc
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.exception)
        # And no product for vet only either
        line.product_id = self.prod_vet_only
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_client_veterinary_wholesale(self):
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        warns = self.env["exception.rule"].search([("warning_only", "=", 1)])
        warns.write({"active": 0})
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_callcenter"
        )
        # Food and gear and medoc are allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.exception)
        # And vet only product as well, for sure
        line.product_id = self.prod_vet_only
        self.assertFalse(line.exception)
        # But not human medoc
        line.product_id = self.prod_medoc_human
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_client_export(self):
        """Test client export sale order limitations."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_customerexport"
        )
        # Food and gear is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        # Medoc for parapharmacy are ok as well
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.exception)
        # But not other medoc
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        line.product_id = self.prod_medoc_vet_belge
        self.assertTrue(line.exception)
        # And not the one for belgium only
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.exception)
        # And no product for vet only either
        line.product_id = self.prod_vet_only
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_med_export(self):
        """Test client medicament export sale order limitations."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_med_export"
        )
        # Food and gear is allowed
        line = self.so1.order_line[0]
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        # Medoc veterinary belge ok
        line.product_id = self.prod_medoc_vet_belge
        self.assertFalse(line.exception)
        # Medoc for parapharmacy are ok as well
        line.product_id = self.prod_medoc_pharma
        self.assertFalse(line.exception)
        # No Psychotropes Annexe III
        line.product_id = self.prod_psycho_III
        self.assertTrue(line.exception)
        # But not other medoc
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        # And not the one for belgium only
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.exception)
        # And no stup
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_customer_only_material(self):
        """Test customer only materials."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_only_material"
        )
        line = self.so1.order_line[0]
        # Gear is allowed
        line.product_id = self.prod_matos
        self.assertFalse(line.exception)
        # Food is not allowed
        line.product_id = self.prod_food
        self.assertTrue(line.exception)
        # No medicine allowed
        line.product_id = self.prod_medoc
        self.assertTrue(line.exception)
        # Medoc veterinary belge ok
        line.product_id = self.prod_medoc_vet_belge
        self.assertTrue(line.exception)
        # Medoc for parapharmacy are ok as well
        line.product_id = self.prod_medoc_pharma
        self.assertTrue(line.exception)
        # No Psychotropes Annexe III
        line.product_id = self.prod_psycho_III
        self.assertTrue(line.exception)
        # But not other medoc
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        # And not the one for belgium only
        line.product_id = self.prod_medoc_belge_only
        self.assertTrue(line.exception)
        # And no stup
        line.product_id = self.prod_stup
        self.assertTrue(line.exception)
        rules.write({"active": 0})

    def test_exception_warning_not_blocking(self):
        """Check that a warning exception does not block confirmation."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        self.warning = self.env["exception.rule"].create(
            {
                "model": "sale.order.line",
                "name": "Exception Warning Test",
                "code": "failed=True",
                "active": True,
                "warning_only": True,
            }
        )
        self.so1.action_confirm()
        self.assertEqual(self.so1.state, "sale")

    def test_exception_is_blocking(self):
        """Check that a warning exception does not block confirmation."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        self.warning = self.env["exception.rule"].create(
            {
                "model": "sale.order.line",
                "name": "Exception Test",
                "code": "failed=True",
                "active": True,
                "warning_only": False,
            }
        )
        self.so1.action_confirm()
        self.assertNotEqual(self.so1.state, "sale")

    def test_exception_warning_psychotropic_product(self):
        """Check sale order line message for psychotropic products."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        exception = self.env.ref("specific_sale.warning_psychotropic")
        line = self.so1.order_line[0]
        line.product_id = self.prod_psycho_III
        self.assertTrue(exception.warning_text in line.warning_text)

    def test_exception_warning_stupefiant_vet_product(self):
        """Check sale order line message for psychotropic products."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        exception = self.env.ref("specific_sale.warning_stupefiant_vet")
        line = self.so1.order_line[0]
        line.product_id = self.prod_stupefiant_vet
        self.assertTrue(exception.warning_text in line.warning_text)

    def test_exceptions_by_phone(self):
        """Check psychotropic are not oredered on the phone."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        warning = self.env.ref("specific_sale.warning_psychotropic")
        psycotropic = self.env.ref("specific_sale.no_psychotropic_by_phone")
        vet = self.env.ref("specific_sale.no_stupefiant_vet_by_phone")
        self.partner.alcyon_category_id = self.env.ref(
            "specific_partner.partner_category_pharmacy"
        )
        line = self.so1.order_line[0]
        line.order_id.sale_channel = "fax"
        line.product_id = self.prod_psycho_III
        # Sale order by fax the line should only have the warning displayed
        self.assertEqual(line.exception, warning.description)
        # Sale order by phone should have the exception
        line.order_id.sale_channel = "phone"
        # Switch product to trigger exception checking
        line.product_id = self.prod_food
        line.product_id = self.prod_psycho_III
        self.assertEqual(line.exception, psycotropic.description)
        line.product_id = self.prod_food
        self.assertFalse(line.exception)
        line.product_id = self.prod_stupefiant_vet
        self.assertEqual(line.exception, vet.description)

    def test_no_backorder_rule(self):
        """Check the no backorder rule.

        A customer can be configured to not accept a sale order which implies
        some back order.
        """
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        # This rule is exist but is not activated in the app
        rule_qty_at_zero = self.env.ref(
            "specific_sale.no_line_at_zero", raise_if_not_found=False
        )
        if rule_qty_at_zero:
            rule_qty_at_zero.active = 0
        no_backorder_rule = self.env.ref("specific_sale.no_backorder")
        self.partner.is_sale_back_order_accepted = False
        line = self.so1.order_line[0]
        line.product_uom_qty = 234
        self.assertEqual(no_backorder_rule.description, line.exception)
        # If quantity ordered is zero exception should not be raised
        line.product_uom_qty = 0
        self.assertEqual("", line.exception)
        # And if it is set to a positive number raised again
        line.product_uom_qty = 234
        self.assertEqual(no_backorder_rule.description, line.exception)
        # Check customer accept back order
        self.partner.is_sale_back_order_accepted = True
        line.product_uom_qty = 534
        self.assertEqual("", line.exception)

    def test_exception_warning_provision_on_order(self):
        """Check the warning provision on order."""
        rules = self.env["exception.rule"].search([("active", "=", 1)])
        rules.write({"active": 0})
        exception = self.env.ref("specific_sale.provision_on_order")
        exception.write({"active": 1})
        line = self.so1.order_line[0]
        line.product_id = self.prod_provision_on_sale
        self.assertTrue(exception.warning_text in line.warning_text)

    def test_exception_warning_cascade_importation(self):
        """Check sale order line message for cascade importation products."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        exception = self.env.ref("specific_sale.warning_cascade_import")
        line = self.so1.order_line[0]
        line.product_id = self.prod_cascade_import
        self.assertTrue(exception.warning_text in line.warning_text)

    def test_exception_warning_medoc_human(self):
        """Check sale order line message for human medicicine."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        exception = self.env.ref("specific_sale.warning_human_medoc")
        line = self.so1.order_line[0]
        line.product_id = self.prod_medoc_human
        self.assertTrue(exception.warning_text in line.warning_text)

    def test_exception_out_of_stock_at_supplier(self):
        """Check warning for out of stock at supplier level."""
        rules = self.env["exception.rule"].search([("active", "=", 0)])
        rules.write({"active": 1})
        exception = self.env.ref("specific_sale.warning_supplier_break")
        line = self.so1.order_line[0]
        # Set the Out Of Stock At Supplier Level state on the product
        # And switch the product to trigger the exceptions
        self.prod1.state_id = self.env.ref("specific_purchase.product_state_h")
        line.product_id = self.prod_medoc_human
        line.product_id = self.prod1
        self.assertTrue(exception.warning_text in line.warning_text)
        # With some inventory there should be no warning
        stock_location = self.env.ref("stock.stock_location_stock")
        inventory = self.env["stock.inventory"].create(
            {"name": "Test", "location_id": stock_location.id}
        )
        inventory.prepare_inventory()
        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": self.prod1.product_variant_id.id,
                "product_qty": 1000,
                "location_id": stock_location.id,
            }
        )
        inventory.action_done()
        # Cache refreshing needed for the back order calculation to work ?
        self.prod1.refresh()
        line.product_id = self.prod_medoc_human
        line.product_id = self.prod1
        self.assertTrue(not line.warning_text)
