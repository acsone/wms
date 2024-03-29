# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.queue_job.tests.common import JobMixin, trap_jobs

from .common import AccountInvoicePrintCommon


class TestAccountInvoicePrintWizard(AccountInvoicePrintCommon, JobMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["account.invoice.sent"]

    def test_wizard_print(self):
        """
        Data:

            partner_0 with 2 invoices and invoice_sending_method "post"
            partner_1 with 2 invoice and invoice_sending_method "mail"
            partner_2 with 2 invoice and invoice_sending_method "post"
        Test case:
            Generate the all the invoices before launching the wizard
            Print all the invoices with the wizard
        Expected result:
            * 4 invoices are printed (partner_0 and partner_2) for sending
            method "post"
        """
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})

        self.assertEqual(4, wizard.count_print)

        with trap_jobs() as trap:
            wizard.button_print()
            trap.assert_jobs_count(1)
            trap.enqueued_jobs[0].perform()
        self.assertAttachementCount(self.invoices, 4)

    def test_wizard_email(self):
        """
        Data:

            partner_0 with 2 invoices and invoice_sending_method "post"
            partner_1 with 2 invoice and invoice_sending_method "mail"
            partner_2 with 2 invoice and invoice_sending_method "post"
        Test case:
            Generate the all the invoices before launching the wizard
            Generate the mail sending
        Expected result:
            * 2 invoices are in attachments
            * 2 mails are sent
        """
        mail_count = self.env["mail.mail"].search_count([])
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})

        self.assertEqual(2, wizard.count_email)

        with trap_jobs() as trap:
            wizard.button_email()
            trap.assert_jobs_count(1)
            with trap_jobs() as trap_mail:
                trap.enqueued_jobs[0].perform()
                trap_mail.assert_jobs_count(2)
                for job in trap_mail.enqueued_jobs:
                    job.perform()
        # Mail template has attachment field value set
        self.assertAttachementCount(self.invoices, 2)
        mail_count_after = self.env["mail.mail"].search_count([]) - mail_count
        self.assertEqual(2, mail_count_after)

    def test_wizard_mark_as_sent(self):
        """
        Data:

            partner_0 with 2 invoices and invoice_sending_method "post"
            partner_1 with 2 invoice and invoice_sending_method "mail"
            partner_2 with 2 invoice and invoice_sending_method "post"
        Test case:
            Generate the all the invoices before launching the wizard
            Mark them as sent
        Expected result:
            * Invoices should be marked as sent
            * No attachment should have been generated
        """
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})
        self.assertEqual(2, wizard.count_email)
        self.assertEqual(4, wizard.count_print)
        wizard.button_mark_only()
        self.assertTrue(all(invoice.is_move_sent for invoice in self.invoices))
        self.assertAttachementCount(self.invoices, 0)

        # Check the counters
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})

        self.assertEqual(0, wizard.count_email)
        self.assertEqual(0, wizard.count_print)

    def test_wizard_related(self):
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})
        counter = self.job_counter()
        wizard.button_email()
        job = counter.search_created()
        invoices_to_print = self.invoices._filter_send_invoice("mail")
        action = job.related_action_open_invoice()
        domain = action.get("domain")
        self.assertListEqual(invoices_to_print.ids, domain[0][2])
