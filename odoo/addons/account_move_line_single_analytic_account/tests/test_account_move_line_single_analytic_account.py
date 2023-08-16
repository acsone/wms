from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAccount(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.env.user.groups_id += cls.env.ref("analytic.group_analytic_accounting")

        # By default, tests are run with the current user set on the first company.
        cls.env.user.company_id = cls.company_data["company"]

        cls.default_plan = cls.env["account.analytic.plan"].create(
            {"name": "Default", "company_id": False}
        )
        cls.analytic_account_a = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_a",
                "plan_id": cls.default_plan.id,
                "company_id": False,
            }
        )
        cls.analytic_account_b = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_b",
                "plan_id": cls.default_plan.id,
                "company_id": False,
            }
        )

    def test_single_analytic_account(self):
        """
        When set a valid analytic_distribution is 1 analytic account at 100%.

        If we try to set 2 accounts or 1 account not at 100% we get a ValidationError
        """
        out_invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": self.partner_a.id,
                    "date": "2017-01-01",
                    "invoice_date": "2017-01-01",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": self.product_a.id,
                                "price_unit": 200.0,
                            }
                        )
                    ],
                }
            ]
        )
        move_line = out_invoice.invoice_line_ids[0]
        self.assertFalse(move_line.analytic_distribution)
        # set a valid distribution: 1 analytic account at 100%
        move_line.analytic_distribution = {self.analytic_account_a.id: 100}
        self.assertEqual(
            move_line.analytic_distribution, {f"{self.analytic_account_a.id}": 100}
        )
        # set an invalid distribution: 2 analytic accounts for a total of 100%
        with self.assertRaises(ValidationError):
            move_line.analytic_distribution = {
                self.analytic_account_a.id: 50,
                self.analytic_account_b.id: 50,
            }
        self.assertEqual(
            move_line.analytic_distribution, {f"{self.analytic_account_a.id}": 100}
        )  # no change
        # set another invalid distribution: 1 analytic account at 50%
        with self.assertRaises(ValidationError):
            move_line.analytic_distribution = {
                self.analytic_account_a.id: 50,
            }
        self.assertEqual(
            move_line.analytic_distribution, {f"{self.analytic_account_a.id}": 100}
        )  # no change
