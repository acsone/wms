# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.alc_account_test_common.tests.common import AlcCommonTestAccount


@tagged("post_install", "-at_install")
class AccountInvoicePrintCommon(
    HttpCase, AccountTestInvoicingCommon, AlcCommonTestAccount
):
    @classmethod
    def setUpClass(cls):
        """
        Create 3 partners with 2 invoices by partner.

        Only partner 0 and 2 should received invoice by letter
        """
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, force_report_rendering=True
            )
        )

        cls.AccountAccount = cls.env["account.account"]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.AccountInvoicePrint = cls.env["account.invoice.print"]
        cls.AccountJournal = cls.env["account.journal"]
        cls.email = cls.env.ref("account_invoice_transmit_method.mail")
        cls.post = cls.env.ref("account_invoice_transmit_method.post")

        # INSTANCES

        # Instance partner
        # only partner 0 and 2 should received invoice by letter
        for i in range(3):
            partner = cls.env["res.partner"].create(
                {
                    "name": "TEST {i}",
                    "ref": "{i}",
                    "customer_invoice_transmit_method_id": cls.post.id
                    if not i % 2
                    else cls.email.id,
                }
            )
            setattr(cls, f"partner_{i}", partner)

        # Instance: company
        cls.company = cls.env.ref("base.main_company")

        # Instance: account type (receivable)
        # cls.type_recv = cls.env.ref("account.data_account_type_receivable")

        # # Instance: account type (payable)
        # cls.type_payable = cls.env.ref("account.data_account_type_payable")

        # Instance: account (receivable)
        cls.account_recv = cls.company_data["default_account_receivable"]

        # Instance: account (payable)
        cls.account_payable = cls.company_data["default_account_payable"]

        # Instance: partner
        cls.partner = cls.env.ref("base.res_partner_2")

        # Instance: journal
        cls.journal = cls.company_data["default_journal_sale"]

        # Instance: product
        cls.product = cls.env.ref("product.product_product_4")

        cls.invoices = cls.AccountMove.browse()
        # create 2 invoices for each partner
        for i in range(2):
            for p in range(3):
                partner = getattr(cls, f"partner_{p}")
                # Instance: invoice
                invoice = cls.AccountMove.create(
                    {
                        "partner_id": partner.id,
                        "move_type": "out_invoice",
                        "invoice_date": "2019-01-21",
                        "date": "2019-01-21",
                        "invoice_line_ids": [
                            Command.create(
                                {
                                    "name": f"test {i} {p}",
                                    "price_unit": 100.00 * p * i,
                                    "quantity": 1,
                                    "product_id": cls.product.id,
                                }
                            )
                        ],
                    }
                )
                setattr(cls, f"partner_{p}_invoice_{i}", invoice)
                cls.invoices |= invoice
        cls.invoices.action_post()

    def filter(self, record):
        # required to mute logger
        return 0

    def _print_invoices(self, invoices):
        invoice_print = self.AccountInvoicePrint.create(
            {"invoice_ids": [(6, 0, invoices.ids)]}
        )
        return invoice_print.generate_report()

    def _sort_invoices(self, invoices):
        return invoices.sorted(
            lambda i: (i.partner_id.name and i.partner_id.name.lower(), i.name)
        )

    def _get_invoice_ids_from_invoices_path(self, invoices_path):
        return [int(p.split(".")[1]) for p in invoices_path]

    def _generate_invoice_document(self, invoice):
        self.env["ir.actions.report"]._render_qweb_pdf(
            "account.report_invoice", res_ids=invoice.ids
        )
        # self.env["report"].get_pdf(invoice.ids, "account.report_invoice")

    def assertAttachementCount(self, instances, count):
        attachement_count = self.env["ir.attachment"].search_count(
            [("res_id", "in", instances.ids), ("res_model", "=", instances._name)]
        )
        self.assertEqual(count, attachement_count)
