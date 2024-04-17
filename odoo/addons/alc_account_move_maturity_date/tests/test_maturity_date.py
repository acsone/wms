# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.alc_account_test_common.tests.common import AlcCommonTestAccount


@tagged("post_install", "-at_install")
class TestAccountMaturityDate(AlcCommonTestAccount, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.journal = cls.company_data["default_journal_misc"]
        cls.journal.use_move_date_as_date_maturity = True
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier",
            }
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Customer",
            }
        )

    @classmethod
    def _create_move(cls):
        tax_repartition_line = cls.company_data[
            "default_tax_sale"
        ].refund_repartition_line_ids.filtered(
            lambda line: line.repartition_type == "tax"
        )
        cls.test_move = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "date": fields.Date.from_string("2016-01-01"),
                "journal_id": cls.journal.id,
                "line_ids": [
                    (
                        0,
                        None,
                        {
                            "name": "revenue line 1",
                            "account_id": cls.company_data[
                                "default_account_revenue"
                            ].id,
                            "debit": 500.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "name": "revenue line 2",
                            "account_id": cls.company_data[
                                "default_account_revenue"
                            ].id,
                            "debit": 1000.0,
                            "credit": 0.0,
                            "tax_ids": [
                                (6, 0, cls.company_data["default_tax_sale"].ids)
                            ],
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "name": "tax line",
                            "account_id": cls.company_data[
                                "default_account_tax_sale"
                            ].id,
                            "debit": 150.0,
                            "credit": 0.0,
                            "tax_repartition_line_id": tax_repartition_line.id,
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "name": "counterpart line",
                            "account_id": cls.company_data[
                                "default_account_expense"
                            ].id,
                            "debit": 0.0,
                            "credit": 1650.0,
                        },
                    ),
                ],
            }
        )

    @classmethod
    def _create_move_compensatory(cls):
        cls.test_move = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "date": fields.Date.from_string("2016-01-01"),
                "journal_id": cls.journal.id,
                "line_ids": [
                    (
                        0,
                        None,
                        {
                            "name": "Customers",
                            "account_id": cls.company_data[
                                "default_account_revenue"
                            ].id,
                            "partner_id": cls.customer.id,
                            "debit": 500.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "name": "Suppliers",
                            "account_id": cls.company_data[
                                "default_account_expense"
                            ].id,
                            "partner_id": cls.supplier.id,
                            "debit": 0.0,
                            "credit": 500.0,
                        },
                    ),
                ],
            }
        )

    def test_maturity_date(self):
        # The parameter is activated on journal level
        # The maturity date should be equal to the move date
        self._create_move()
        for line in self.test_move.line_ids:
            self.assertEqual(line.date, line.date_maturity)

    def test_maturity_date_compensatory(self):
        # The parameter is activated on journal level
        # The maturity date should be equal to the move date
        self._create_move_compensatory()
        for line in self.test_move.line_ids:
            self.assertEqual(line.date, line.date_maturity)

    def test_no_maturity_date(self):
        # The parameter is not activated on journal level
        # The maturity date should be void
        # Test that manual modification is allowed
        self.journal.use_move_date_as_date_maturity = False
        self._create_move()
        for line in self.test_move.line_ids:
            self.assertFalse(line.date_maturity)

        # Test modifying manually date_maturity
        today = fields.Date.today()
        self.test_move.line_ids[0].date_maturity = today
        self.assertEqual(today, self.test_move.line_ids[0].date_maturity)
