# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestSaleOrderException(TransactionCase):

    def setUp(self):
        super(TestSaleOrderException, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.prod1 = self.env.ref('product.product_product_1')
        self.prod1.categ_id = self.env.ref(
            'specific_data.product_categ_materiel')
        self.prod_food = self.env['product.product'].create({
            'name': 'I am some food, yam',
            'categ_id': self.env.ref(
                'specific_data.product_categ_ali_divers').id
        })
        self.prod_stup = self.env['product.product'].create({
            'name': 'I am a stupefiant',
            'categ_id': self.env.ref(
                'specific_data.product_categ_stupefiant').id
        })
        self.prod_matos = self.env['product.product'].create({
            'name': 'I am some gear',
            'categ_id': self.env.ref(
                'specific_data.product_categ_mat_instrumentation').id
        })
        self.prod_medoc_pharma = self.env['product.product'].create({
            'name': 'I am  a medoc pharmacy',
            'categ_id': self.env.ref(
                'specific_data.product_categ_parapharmacie').id
        })
        self.prod_medoc_human = self.env['product.product'].create({
            'name': 'I am a human medoc',
            'categ_id': self.env.ref('specific_data.product_categ_humain').id
        })
        self.prod_medoc_vet_belge = self.env['product.product'].create({
            'name': 'I am a beligum veterinarian product',
            'categ_id': self.env.ref(
                'specific_data.product_categ_vet_belges').id
        })
        self.prod_medoc_belge_only = self.env['product.product'].create({
            'name': 'I am a beligum medoc only',
            'categ_id': self.env.ref(
                'specific_data.product_categ_parapharmacie').id,
            'belgium_only': True,
        })
        self.prod_vet_only = self.env['product.product'].create({
            'name': 'I am for veterinary only',
            'categ_id': self.env.ref(
                'specific_data.product_categ_ali_divers').id,
            'veterinary_only': True,
        })
        self.prod_psycho_III = self.env['product.product'].create({
            'name': 'I am a medoc belge Psychotropes III',
            'categ_id': self.env.ref(
                'specific_data.product_categ_psychotropes_25').id,
        })
        self.prod_medoc = self.env['product.product'].create({
            'name': 'Base medicine category',
            'categ_id': self.env.ref(
                'specific_data.product_categ_medoc').id,
        })
        self.delivery = self.env['delivery.carrier'].search(
                [('free_if_more_than', '=', False)], limit=1)
        self.so1 = self.env['sale.order'].create({
            'esb_ref': 'ref_123',
            'partner_id': self.partner.id,
            'date_order': '2018-01-29',
            'sale_channel': 'fax',
            'carrier_id': self.delivery.id,
            'client_order_ref': 'whatever the client want',
            'delivery_price': 23.5,
            'suite_name': '0123434234',
            'order_line': [
                (0, 0, {
                    'sequence': 1,
                    'name': self.prod1.name,
                    'product_id': self.prod1.id,
                    'product_uom_qty': 7,
                })],
        })

    def test_client_alcyonnaire(self):
        # Need the correct category for this one ?
        self.partner.alcyon_category_id = self.env.ref(
           'specific_partner.partner_category_alcyonaire')
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

    def test_client_veterinary_with_depot(self):
        self.partner.alcyon_category_id = self.env.ref(
           'specific_partner.partner_category_veterinary')
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

    def test_client_students(self):
        "Test customer students"
        self.partner.alcyon_category_id = self.env.ref(
                'specific_partner.partner_category_student')
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

    def test_client_pharmacist_wholesale_human(self):
        """ """
        self.partner.alcyon_category_id = self.env.ref(
                'specific_partner.partner_category_pharmacy')
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

    def test_client_veterinary_wholesale(self):
        """ """
        self.partner.alcyon_category_id = self.env.ref(
                'specific_partner.partner_category_callcenter')
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

    def test_client_export(self):
        """Test client export sale order limitations."""
        self.partner.alcyon_category_id = self.env.ref(
                'specific_partner.partner_category_customerexport')
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

    def test_med_export(self):
        """Test client medicament export sale order limitations."""
        self.partner.alcyon_category_id = self.env.ref(
                'specific_partner.partner_category_med_export')
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

    def test_customer_only_material(self):
        """Test customer only materials."""
        self.partner.alcyon_category_id = self.env.ref(
                'specific_partner.partner_category_only_material')
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
