# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestAlcDocumentsPrices


class TestAlcDocumentsPricesFlow(TestAlcDocumentsPrices):
    def test_flow(self):
        self.partner._process_dossier()
        # then: we have pricelist files
        self.assertEqual(self.partner.alc_document_count, 2)

        # given
        partner = self.partner.with_context(test_queue_job_no_delay=True)
        # when
        partner.supplier_promotion_sale_allowed = True
        # then: we also have discount files
        self.assertEqual(self.partner.alc_document_count, 4)
        # then: they are all empty
        domain_partner = [("partner_id", "=", partner.id)]
        documents_partner = self.alc_document_model.search(domain_partner)
        self.assertFalse(documents_partner.mapped("attachment_id"))

        domain_base = [("format", "=", "csv"), ("partner_id", "=", partner.id)]

        # given
        domain_pricelist = domain_base + [("compute", "=", "pricelist")]
        document_pricelist = self.alc_document_model.search(domain_pricelist)
        # when
        document_pricelist._get_data()
        # then
        self.assertTrue(document_pricelist.attachment_id)

        # given
        domain_discount = domain_base + [("compute", "=", "discount")]
        document_discount = self.alc_document_model.search(domain_discount)
        # when
        document_discount._get_data()
        # then
        self.assertTrue(document_discount.attachment_id)
