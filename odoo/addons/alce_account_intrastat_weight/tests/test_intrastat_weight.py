# Copyright 2023 ACSONE SA/NV
# License Other proprietary
from freezegun import freeze_time

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account_reports.tests.common import TestAccountReportsCommon


@tagged("post_install", "-at_install")
class TestIntrastatReport(TestAccountReportsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Create a fictional intrastat country
        country = cls.env["res.country"].create(
            {
                "name": "Squamuglia",
                "code": "SQ",
                "intrastat": True,
            }
        )
        cls.company_data["company"].country_id = country
        cls.report = cls.env.ref("account_intrastat.intrastat_report")
        cls.partner_a = cls.env["res.partner"].create(
            {"name": "Yoyodyne BE", "country_id": cls.env.ref("base.be").id}
        )

        # A product that has no supplementary unit
        cls.product_no_supplementary_unit = cls.env["product.product"].create(
            {
                "name": "stamp collection",
                "intrastat_code_id": cls.env.ref(
                    "account_intrastat.commodity_code_2018_97040000"
                ).id,
                "intrastat_supplementary_unit_amount": None,
            }
        )
        # A product that has a supplementary unit of the type "p/st"
        cls.product_unit_supplementary_unit = cls.env["product.product"].create(
            {
                "name": "rocket",
                "intrastat_code_id": cls.env.ref(
                    "account_intrastat.commodity_code_2018_93012000"
                ).id,
                "intrastat_supplementary_unit_amount": 1,
            }
        )
        # A product that has a supplementary unit of the type "100 p/st"
        cls.product_100_unit_supplementary_unit = cls.env["product.product"].create(
            {
                "name": "Imipolex G Tooth",
                "intrastat_code_id": cls.env.ref(
                    "account_intrastat.commodity_code_2018_90212110"
                ).id,
                "intrastat_supplementary_unit_amount": 0.01,
            }
        )
        # A product that has a supplementary unit of the type "m"
        cls.product_metre_supplementary_unit = cls.env["product.product"].create(
            {
                "name": "Proper Gander Film",
                "intrastat_code_id": cls.env.ref(
                    "account_intrastat.commodity_code_2018_37061020"
                ).id,
                "intrastat_supplementary_unit_amount": 1,
                "uom_id": cls.env.ref("uom.product_uom_meter").id,
                "uom_po_id": cls.env.ref("uom.product_uom_meter").id,
            }
        )
        # A product with the product origin country set to spain
        cls.spanish_rioja = cls.env["product.product"].create(
            {
                "name": "rioja",
                "intrastat_code_id": cls.env.ref(
                    "account_intrastat.commodity_code_2018_22042176"
                ).id,
                "intrastat_origin_country_id": cls.env.ref("base.es").id,
            }
        )

        code_vals = [
            {"type": type, "name": f"{type}"}
            for type in ("commodity", "transaction", "region")
        ]
        cls.intrastat_codes = {}
        # 100 - commodity
        # 101 - transaction
        # 102 - region
        create_vals_list = []
        for i, vals in enumerate(code_vals, 100):
            vals["code"] = str(i)
            create_vals_list.append(vals)
        cls.intrastat_codes = {
            x.name: x
            for x in cls.env["account.intrastat.code"].sudo().create(create_vals_list)
        }

        cls.company_data["company"].intrastat_region_id = cls.intrastat_codes[
            "region"
        ].id

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 100.0,
                "standard_price": 80.0,
                "property_account_income_id": cls.company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_id": cls.company_data[
                    "default_account_expense"
                ].id,
                "taxes_id": [Command.set(cls.tax_sale_a.ids)],
                "supplier_taxes_id": [Command.set(cls.tax_purchase_a.ids)],
                "intrastat_code_id": cls.intrastat_codes["commodity"].id,
                "weight": 0.3,
            }
        )

        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 150.0,
                "standard_price": 120.0,
                "property_account_income_id": cls.company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_id": cls.company_data[
                    "default_account_expense"
                ].id,
                "taxes_id": [Command.set(cls.tax_sale_a.ids)],
                "supplier_taxes_id": [Command.set(cls.tax_purchase_a.ids)],
                "intrastat_code_id": cls.intrastat_codes["commodity"].id,
                "weight": 0.6,
            }
        )

        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "product_3",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 950.0,
                "property_account_income_id": cls.company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_id": cls.company_data[
                    "default_account_expense"
                ].id,
                "taxes_id": [Command.set(cls.tax_sale_a.ids)],
                "supplier_taxes_id": [Command.set(cls.tax_purchase_a.ids)],
                "intrastat_code_id": cls.intrastat_codes["commodity"].id,
                "weight": 0.0,
            }
        )

    @classmethod
    def _create_invoices(cls, code_type=None):
        moves = cls.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": cls.partner_a.id,
                    "invoice_date": "2022-01-01",
                    "intrastat_country_id": cls.env.ref("base.nl").id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "line_1",
                                "product_id": cls.product_1.id,
                                "intrastat_transaction_id": cls.intrastat_codes[
                                    code_type
                                ].id
                                if code_type
                                else None,
                                "product_uom_id": cls.env.ref(
                                    "uom.product_uom_unit"
                                ).id,
                                "quantity": 1.0,
                                "account_id": cls.company_data[
                                    "default_account_revenue"
                                ].id,
                                "price_unit": 80.0,
                                "tax_ids": [],
                            }
                        ),
                        Command.create(
                            {
                                "name": "line_2",
                                "product_id": cls.product_2.id,
                                "intrastat_transaction_id": cls.intrastat_codes[
                                    code_type
                                ].id
                                if code_type
                                else None,
                                "product_uom_id": cls.env.ref(
                                    "uom.product_uom_unit"
                                ).id,
                                "quantity": 2.0,
                                "account_id": cls.company_data[
                                    "default_account_revenue"
                                ].id,
                                "price_unit": 120.0,
                                "tax_ids": [],
                            }
                        ),
                    ],
                },
                {
                    "move_type": "in_invoice",
                    "partner_id": cls.partner_a.id,
                    "invoice_date": "2022-01-01",
                    "intrastat_country_id": cls.env.ref("base.nl").id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "line_3",
                                "product_id": cls.product_3.id,
                                "intrastat_transaction_id": cls.intrastat_codes[
                                    code_type
                                ].id
                                if code_type
                                else None,
                                "product_uom_id": cls.env.ref(
                                    "uom.product_uom_unit"
                                ).id,
                                "quantity": 1.0,
                                "account_id": cls.company_data[
                                    "default_account_expense"
                                ].id,
                                "price_unit": 950.0,
                                "tax_ids": [],
                            }
                        ),
                    ],
                },
            ]
        )
        moves.action_post()

    @freeze_time("2022-02-01")
    def test_intrastat_report_values(self):
        self._create_invoices(code_type="transaction")
        options = self._generate_options(self.report, "2022-01-01", "2022-01-31")
        lines = self.report._get_lines(options)

        # Check weight for product 3 == 0.01
        self.assertLinesValues(
            lines,
            # 1/system, 2/country code, 3/transaction code, 4/region code,
            # 5/commodity code, 6/origin country, 10/weight, 12/value
            [1, 2, 3, 4, 5, 6, 10, 12],
            [
                # account.move (invoice) 1
                ("19 (Dispatch)", "Netherlands", "101", "102", "100", None, 0.3, 80.0),
                ("19 (Dispatch)", "Netherlands", "101", "102", "100", None, 1.2, 240.0),
                # account.move (bill) 2
                ("29 (Arrival)", "Netherlands", "101", "102", "100", None, 0.01, 950.0),
            ],
        )
