# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import enum
from unittest import mock

from .common import TestAlcDocumentsPrices


class SupplierDiscountType(enum.Enum):
    """Enum for the type of supplier discount."""

    PROMOTION = "promotion"
    DISCOUNT = "discount"


class TestAlcDocumentsPricesFlow(TestAlcDocumentsPrices):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.partner.with_context(queue_job__no_delay=True)
        cls.partner.supplier_promotion_sale_allowed = False
        cls.partner.partner_type = "guest"

    def test_flow(self):
        self.partner._process_dossier()
        # then: we have pricelist files
        self.assertEqual(self.partner.alc_document_count, 2)

        # given
        partner = self.partner.with_context(queue_job__no_delay=True)
        # when
        partner.supplier_promotion_sale_allowed = True
        # then: we also have discount files
        self.assertEqual(self.partner.alc_document_count, 4)
        # then: they are all empty
        domain_partner = [("partner_id", "=", partner.id)]
        documents_partner = self.alc_document_model.search(domain_partner)
        self.assertFalse(documents_partner.mapped("attachment_id"))
        for document in documents_partner:
            self.assertFalse(document.document_date)

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
        # even after generation, document_date is not set
        for document in documents_partner:
            self.assertFalse(document.document_date)

    def _get_discount_data(
        self,
        supplier_discount_type: SupplierDiscountType,
        only_for_veterinaries,
        partner=None,
    ):
        if not partner:
            partner = self.partner
        flattened_data = self._example_product_flattened_data()
        if supplier_discount_type == SupplierDiscountType.PROMOTION:
            flattened_data["has_supplier_promotion"] = True
            flattened_data[
                "supplier_promotion_only_for_veterinaries"
            ] = only_for_veterinaries
        elif supplier_discount_type == SupplierDiscountType.DISCOUNT:
            flattened_data["supplier_discount_discount_sale"] = 10
            flattened_data[
                "supplier_discount_only_for_veterinaries"
            ] = only_for_veterinaries

        return_value = (r for r in [self._wrap_flattened_data(flattened_data)])
        domain_base = [("format", "=", "csv"), ("partner_id", "=", partner.id)]
        domain_discount = domain_base + [("compute", "=", "discount")]
        document_discount = self.alc_document_model.search(domain_discount)
        with self.mock_product_data(return_value=return_value):
            return document_discount._get_data().decode("utf-8")

    def test_supplier_promotion_guest(self):
        self.partner.partner_type = "guest"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.PROMOTION,
            only_for_veterinaries=False,
        )
        self.assertIn("Produits GRATUITS", csv)

    def test_supplier_promotion_only_veterinary_guest(self):
        self.partner.partner_type = "guest"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.PROMOTION,
            only_for_veterinaries=True,
        )
        self.assertNotIn("Produits GRATUITS", csv)

    def test_supplier_promotion_only_veterinary_veterinary(self):
        self.partner.partner_type = "veterinary"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.PROMOTION,
            only_for_veterinaries=True,
        )
        self.assertIn("Produits GRATUITS", csv)

    def test_supplier_promotion_veterinary(self):
        self.partner.partner_type = "veterinary"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.PROMOTION,
            only_for_veterinaries=False,
        )
        self.assertIn("Produits GRATUITS", csv)

    def test_supplier_discount_guest(self):
        self.partner.partner_type = "guest"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.DISCOUNT,
            only_for_veterinaries=False,
        )
        self.assertIn("10% off", csv)

    def test_supplier_discount_only_veterinary_guest(self):
        self.partner.partner_type = "guest"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.DISCOUNT,
            only_for_veterinaries=True,
        )
        self.assertNotIn("10% off", csv)

    def test_supplier_discount_only_veterinary_veterinary(self):
        self.partner.partner_type = "veterinary"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.DISCOUNT,
            only_for_veterinaries=True,
        )
        self.assertIn("10% off", csv)

    def test_supplier_discount_veterinary(self):
        self.partner.partner_type = "veterinary"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.DISCOUNT,
            only_for_veterinaries=False,
        )
        self.assertIn("10% off", csv)

    def test_no_recompute_same_day(self):
        self.partner.partner_type = "veterinary"
        self.partner.supplier_promotion_sale_allowed = True
        csv = self._get_discount_data(
            supplier_discount_type=SupplierDiscountType.PROMOTION,
            only_for_veterinaries=False,
        )
        self.assertIn("Produits GRATUITS", csv)
        # A second call the same dy should not regenerate the document.
        # The system should return the same document.
        with mock.patch.object(
            type(self.env["alc.document"]), "_generate_attachment_file"
        ) as mocked_generate:
            csv = self._get_discount_data(
                supplier_discount_type=SupplierDiscountType.PROMOTION,
                only_for_veterinaries=False,
            )
            self.assertIn("Produits GRATUITS", csv)
            mocked_generate.assert_not_called()
