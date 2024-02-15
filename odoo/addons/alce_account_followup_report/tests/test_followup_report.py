# Copyright 2024 ACSONE SA/NV
# License Other proprietary

from freezegun import freeze_time

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account_reports.tests.common import TestAccountReportsCommon


@tagged("post_install")
class TestAlceAccountFollowupReports(TestAccountReportsCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

    def test_alce_followup_report(self):
        """Test report lines when printing the follow-up report."""
        # Init options.
        report = self.env["account.followup.report"]
        options = {
            "partner_id": self.partner_a.id,
        }

        # 2016-01-01: First invoice, partially paid.

        invoice_1 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "invoice_date": "2016-01-01",
                "partner_id": self.partner_a.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "quantity": 1,
                            "price_unit": 500,
                            "tax_ids": [],
                        }
                    )
                ],
            }
        )
        invoice_1.action_post()

        payment_1 = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2016-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "debit": 0.0,
                            "credit": 200.0,
                            "account_id": self.company_data[
                                "default_account_receivable"
                            ].id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "debit": 200.0,
                            "credit": 0.0,
                            "account_id": self.company_data[
                                "default_journal_bank"
                            ].default_account_id.id,
                        },
                    ),
                ],
            }
        )
        payment_1.action_post()

        (payment_1 + invoice_1).line_ids.filtered(
            lambda line: line.account_id
            == self.company_data["default_account_receivable"]
        ).reconcile()

        with freeze_time("2016-01-01"):
            lines = report._get_followup_report_lines(options)
            self.assertEqual("INV/2016/00001", lines[0].get("name"))
            self.assertEqual(lines[0]["columns"][0]["name"], "01/01/2016")
            self.assertEqual(lines[0]["columns"][1]["name"], "01/01/2016")
            self.assertEqual(lines[0]["columns"][2]["name"], "")
            self.assertIn(
                "300.0",
                lines[0]["columns"][3]["name"],
            )

            self.assertEqual("total", lines[1].get("class"))
            self.assertEqual(lines[1]["columns"][0]["name"], "")
            self.assertEqual(lines[1]["columns"][1]["name"], "")
            self.assertEqual(lines[1]["columns"][2]["name"], "Total Due")
            self.assertIn(
                "300.0",
                lines[0]["columns"][3]["name"],
            )

        # 2016-01-05: Credit note due at 2016-01-10.

        invoice_2 = self.env["account.move"].create(
            {
                "move_type": "out_refund",
                "invoice_date": "2016-01-05",
                "invoice_date_due": "2016-01-10",
                "partner_id": self.partner_a.id,
                "invoice_payment_term_id": False,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "quantity": 1,
                            "price_unit": 200,
                            "tax_ids": [],
                        }
                    )
                ],
            }
        )
        invoice_2.action_post()

        with freeze_time("2016-01-05"):
            lines = report._get_followup_report_lines(options)
            self.assertEqual("RINV/2016/00001", lines[0].get("name"))
            self.assertEqual(lines[0]["columns"][0]["name"], "01/05/2016")
            self.assertEqual(lines[0]["columns"][1]["name"], "01/10/2016")
            self.assertEqual(lines[0]["columns"][2]["name"], "")
            self.assertIn(
                "-200.0",
                lines[0]["columns"][3]["name"],
            )
            self.assertEqual("INV/2016/00001", lines[1].get("name"))
            self.assertEqual(lines[1]["columns"][0]["name"], "01/01/2016")
            self.assertEqual(lines[1]["columns"][1]["name"], "01/01/2016")
            self.assertEqual(lines[1]["columns"][2]["name"], "")
            self.assertIn(
                "300.0",
                lines[1]["columns"][3]["name"],
            )

            self.assertEqual("total", lines[2].get("class"))
            self.assertEqual(lines[2]["columns"][0]["name"], "")
            self.assertEqual(lines[2]["columns"][1]["name"], "")
            self.assertEqual(lines[2]["columns"][2]["name"], "Total Due")
            self.assertIn(
                "100.0",
                lines[2]["columns"][3]["name"],
            )
