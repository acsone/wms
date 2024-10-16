from unittest import mock

from odoo.exceptions import RedirectWarning
from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.models.account_bank_statement import AccountBankStatement
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAlceCodaFile(AccountTestInvoicingCommon):
    @classmethod
    def _create_account_journals(cls, account_numbers: list) -> None:
        for account_number in account_numbers:
            bank = cls.env["res.partner.bank"].create(
                {
                    "acc_number": account_number,
                    "partner_id": cls.env.company.partner_id.id,
                }
            )
            cls.bank_journal.copy({"bank_account_id": bank.id})

    @classmethod
    def _get_new_bank_statements(cls) -> AccountBankStatement:
        return (
            cls.env["account.bank.statement"].search(
                [("company_id", "=", cls.env.company.id)]
            )
            - cls.previous_statements
        )

    @classmethod
    def setUpClass(cls, chart_template_ref="l10n_be.l10nbe_chart_template"):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bank_journal = cls.company_data["default_journal_bank"]
        coda_file_path = "alce_split_coda/test_coda_file/TEST_CODA.COD"
        with file_open(coda_file_path, "rb") as coda_file:
            cls.coda_file = coda_file.read()
        cls.previous_statements = cls.env["account.bank.statement"].search(
            [("company_id", "=", cls.env.company.id)]
        )

    def test_coda_file_import(self):
        account_numbers = ["BE44340030749745", "BE36363158366381", "BE33340030749846"]
        self._create_account_journals(account_numbers)
        self.company_data["default_journal_bank"].create_document_from_attachment(
            self.env["ir.attachment"]
            .create(
                {
                    "mimetype": "application/text",
                    "name": "TEST_CODA.COD",
                    "raw": self.coda_file,
                }
            )
            .ids
        )

        statements = self._get_new_bank_statements()
        self.assertEqual(3, len(statements))

    def test_coda_file_import_unknown(self):
        """Set only two bank accounts for the company."""
        account_numbers = ["BE44340030749745", "BE36363158366381"]
        self._create_account_journals(account_numbers)
        with (
            mock.patch.object(self.env.cr.__class__, "commit") as commit_mock,
            mock.patch.object(self.env.cr.__class__, "savepoint"),
        ):
            commit_mock.side_effect = mock.Mock
            with self.assertRaises(RedirectWarning):
                self.company_data[
                    "default_journal_bank"
                ].create_document_from_attachment(
                    self.env["ir.attachment"]
                    .create(
                        {
                            "mimetype": "application/text",
                            "name": "TEST_CODA.COD",
                            "raw": self.coda_file,
                        }
                    )
                    .ids
                )
        statements = self._get_new_bank_statements()
        self.assertEqual(2, len(statements))
