# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .common import AccountInvoicePrintCommon


class TestAccountInvoicePrint(AccountInvoicePrintCommon):
    def test_00(self):
        """
        Data:

            partner_0 with 2 invoices and invoice_sending_method "letter"
            partner_1 with 2 invoice and invoice_sending_method "email"
            partner_2 with 2 invoice and invoice_sending_method "letter"
        Test case:
            Print all the invoices with the wizard
        Expected result:
            * 4 invoices are printed (partner_0 and partner_2) for sending
            method "letter"
            * invoices are sorted by partner's ref and invoice number
        """
        self._print_invoices(self.invoices)
        self.assertAttachementCount(self.invoices, 4)

    def test_01(self):
        """
        Data:

            partner_0 with 2 invoices and invoice_sending_method "letter"
            partner_1 with 2 invoice and invoice_sending_method "email"
            partner_2 with 2 invoice and invoice_sending_method "letter"
        Test case:
            Generate 1 invoice for partner_0 and 1 for parnter_2 before using the
            wizard (the attachment will therefore already exists when the wizard
            will be called)
            Print all the invoices with the wizard
        Expected result:
            * 4 invoices are printed (partner_0 and partner_2) for sending
            method "letter"
            * invoices are sorted by partner's ref and invoice number
        """
        self.assertAttachementCount(self.invoices, 0)
        self._generate_invoice_document(self.partner_0_invoice_0)
        self._generate_invoice_document(self.partner_2_invoice_1)
        self.assertAttachementCount(self.invoices, 2)
        self._print_invoices(self.invoices)
        self.assertAttachementCount(self.invoices, 4)

    def test_02(self):
        """
        Data:

            partner_0 with 2 invoices and invoice_sending_method "letter"
            partner_1 with 2 invoice and invoice_sending_method "email"
            partner_2 with 2 invoice and invoice_sending_method "letter"
        Test case:
            Change invoice_sending_method to "letter"
            Print all the invoices with the wizard
        Expected result:
            * 6 invoices are printed (partner_0, partner_1 and partner_2)
            * invoices are sorted by partner's ref and invoice number
        """
        self.assertAttachementCount(self.invoices, 0)
        self.partner_1.customer_invoice_transmit_method_id = self.post
        # Generated invoices are computing transmit method only on partner change
        self.invoices._compute_transmit_method_id()
        self._print_invoices(self.invoices)
        self.assertAttachementCount(self.invoices, 6)

    def test_03(self):
        """
        Data:

            partner_0 with 2 invoices and invoice_sending_method "letter"
            partner_1 with 2 invoice and invoice_sending_method "email"
            partner_2 with 2 invoice and invoice_sending_method "letter"
        Test case:
            Generate the allt invoices before launching the wizard
            Print all the invoices with the wizard
        Expected result:
            * 4 invoices are printed (partner_0 and partner_2) for sending
            method "letter"
            * invoices are sorted by partner's ref and invoice number
        """
        self._generate_invoice_document(self.invoices)
        self.assertAttachementCount(self.invoices, 6)
