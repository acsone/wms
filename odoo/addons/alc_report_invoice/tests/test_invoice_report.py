# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestReportInvoice(AccountTestInvoicingCommon, BaseCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref="l10n_be.l10nbe_chart_template")

        external_layout = cls.env.ref("alc_report_base.external_layout_alcyon")
        cls.env.company.external_report_layout_id = external_layout

        cls.sale_obj = cls.env["sale.order"]
        cls.product_obj = cls.env["product.product"]
        cls.apb_group = cls.env.ref("l10n_be_apb_tax.tax_group_apb")
        cls.sale_group = cls.env.ref("l10n_be.tax_group_tva_21")
        cls.sale_group_6 = cls.env.ref("l10n_be.tax_group_tva_6")
        cls.tax_21 = cls.env["account.tax"].search(
            [
                ("type_tax_use", "=", "sale"),
                ("tax_group_id", "=", cls.sale_group.id),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.tax_6 = cls.env["account.tax"].search(
            [
                ("type_tax_use", "=", "sale"),
                ("tax_group_id", "=", cls.sale_group_6.id),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.taxes_apb = cls.env["account.tax"].search(
            [
                ("tax_group_id", "=", cls.apb_group.id),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.taxes_apb.amount = 0.13709
        pricelist = cls.env["product.pricelist"].search(
            [("currency_id", "=", cls.env.company.currency_id.id)], limit=1
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner Test", "property_product_pricelist": pricelist.id}
        )
        # As this module does not depends on stock, create products as service
        cls.product_1 = cls.product_obj.create(
            {"name": "Product 1 APB", "type": "service", "service_type": "manual"}
        )
        # Ensure sale tax is well configured
        cls.product_1.taxes_id = cls.tax_21 | cls.taxes_apb
        cls.product_2 = cls.product_obj.create(
            {"name": "Product 2", "type": "service", "service_type": "manual"}
        )
        cls.product_2.taxes_id = cls.tax_21

    @classmethod
    def _create_product_precision(cls):
        """Create the different products for precision rounding tests."""
        cls.product_p_1 = cls.product_obj.create(
            {
                "name": "Product P 1",
                "type": "service",
                "list_price": 24.50,
                "taxes_id": [
                    Command.link(cls.tax_6.id),
                    Command.link(cls.taxes_apb.id),
                ],
            }
        )
        cls.product_p_2 = cls.product_obj.create(
            {
                "name": "Product P 2",
                "type": "service",
                "list_price": 10.10,
                "taxes_id": [
                    Command.link(cls.tax_6.id),
                    Command.link(cls.taxes_apb.id),
                ],
            }
        )
        cls.product_p_3 = cls.product_obj.create(
            {
                "name": "Product P 3",
                "type": "service",
                "list_price": 9.90,
                "taxes_id": [
                    Command.link(cls.tax_6.id),
                    Command.link(cls.taxes_apb.id),
                ],
            }
        )
        cls.product_p_4 = cls.product_obj.create(
            {
                "name": "Product P 4",
                "type": "service",
                "list_price": 34.45,
                "taxes_id": [
                    Command.link(cls.tax_6.id),
                    Command.link(cls.taxes_apb.id),
                ],
            }
        )
        cls.product_p_5 = cls.product_obj.create(
            {
                "name": "Product P 5",
                "type": "service",
                "list_price": 11.30,
                "taxes_id": [
                    Command.link(cls.tax_6.id),
                    Command.link(cls.taxes_apb.id),
                ],
            }
        )
        cls.product_p_6 = cls.product_obj.create(
            {
                "name": "Product P 6",
                "type": "service",
                "list_price": 9.80,
                "taxes_id": [
                    Command.link(cls.tax_6.id),
                    Command.link(cls.taxes_apb.id),
                ],
            }
        )
        cls.product_p_7 = cls.product_obj.create(
            {
                "name": "Product P 7",
                "type": "service",
                "list_price": 23.85,
                "taxes_id": [
                    Command.link(cls.tax_6.id),
                    Command.link(cls.taxes_apb.id),
                ],
            }
        )
        cls.product_p_delivery = cls.product_obj.create(
            {
                "name": "Product P Delivery",
                "type": "service",
                "list_price": 2.0,
                "taxes_id": [Command.link(cls.tax_21.id)],
            }
        )

    @classmethod
    def _create_sale_order(cls):
        return cls.sale_obj.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "product_uom": cls.product_1.uom_id.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_2.id,
                            "product_uom": cls.product_2.uom_id.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                ],
            }
        )

    @classmethod
    def _create_sale_order_precision(cls):
        """
        This is intended to simulate a real case where rounding precision.

        is causing wrong amount in report (and not in Odoo).
        """
        return cls.sale_obj.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_p_1.id,
                            "product_uom": cls.product_p_1.uom_id.id,
                            "product_uom_qty": 2.0,
                            "discount3": 7.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_p_2.id,
                            "product_uom": cls.product_p_2.uom_id.id,
                            "product_uom_qty": 3.0,
                            "discount2": 10.0,
                            "discount3": 7.0,
                        }
                    ),
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Section 1",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_p_3.id,
                            "product_uom": cls.product_p_3.uom_id.id,
                            "product_uom_qty": 1.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_p_4.id,
                            "product_uom": cls.product_p_4.uom_id.id,
                            "product_uom_qty": 3.0,
                            "discount2": 12.0,
                            "discount3": 7.0,
                        }
                    ),
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Section 2",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_p_5.id,
                            "product_uom": cls.product_p_5.uom_id.id,
                            "product_uom_qty": 1.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_p_6.id,
                            "product_uom": cls.product_p_6.uom_id.id,
                            "product_uom_qty": 2.0,
                            "discount3": 7.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_p_7.id,
                            "product_uom": cls.product_p_7.uom_id.id,
                            "product_uom_qty": 2.0,
                            "discount2": 10.0,
                            "discount3": 7.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_p_delivery.id,
                            "product_uom": cls.product_p_delivery.uom_id.id,
                            "product_uom_qty": 1.0,
                        }
                    ),
                ],
            }
        )

    def test_sale_order_invoice_tax_summary(self):
        sale = self._create_sale_order()
        sale.action_confirm()
        for line in sale.order_line:
            line.qty_delivered = 10.0
        invoice = sale._create_invoices()
        taxes = invoice._get_taxes_summary()
        self.assertDictEqual(
            taxes,
            {
                "apb": [
                    {
                        "rate": "1.37",
                        "base_amount": "10.00\xa0€",
                        "tax_amount": "1.37\xa0€",
                    }
                ],
                "antibiotics": [],
                "apb_total_tax_amount": "1.37 €",
                "apb_total": 1.37,
                "antibiotics_total_tax_amount": "0.00 €",
                "antibiotics_total": 0,
                "invoice": [
                    {"rate": "21.00", "base_amount": "20.00 €", "tax_amount": "4.20 €"}
                ],
                "invoice_total_tax_amount": "4.20 €",
                "invoice_total": 4.2,
                "contribution_total": 0.0,
                "contribution_total_tax_amount": "0.00 €",
                "amount_without_discount": "20.00 €",
                "amount_untaxed_with_contribution": "20.00 €",
            },
        )

    def test_sale_order_invoice_tax_summary_added(self):
        """
        Check manually entered note line does not harm.

        the amounts.
        """
        sale = self._create_sale_order()
        sale.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "display_type": "line_note",
                            "name": "Test",
                        }
                    )
                ]
            }
        )
        sale.action_confirm()
        for line in sale.order_line:
            line.qty_delivered = 10.0
        invoice = sale._create_invoices()
        taxes = invoice._get_taxes_summary()
        self.assertDictEqual(
            taxes,
            {
                "apb": [
                    {
                        "rate": "1.37",
                        "base_amount": "10.00\xa0€",
                        "tax_amount": "1.37\xa0€",
                    }
                ],
                "antibiotics": [],
                "apb_total_tax_amount": "1.37 €",
                "apb_total": 1.37,
                "antibiotics_total_tax_amount": "0.00 €",
                "antibiotics_total": 0,
                "invoice": [
                    {"rate": "21.00", "base_amount": "20.00 €", "tax_amount": "4.20 €"}
                ],
                "invoice_total_tax_amount": "4.20 €",
                "invoice_total": 4.2,
                "contribution_total": 0.0,
                "contribution_total_tax_amount": "0.00 €",
                "amount_without_discount": "20.00 €",
                "amount_untaxed_with_contribution": "20.00 €",
            },
        )

    def test_sale_order_tax_precision(self):
        """
        The amount seems to depends on payment presence on invoice.

        The tax rounding method should be globally
        """
        self.env.company.tax_calculation_rounding_method = "round_globally"
        self.partner.property_payment_term_id = self.env.ref(
            "account.account_payment_term_15days"
        )
        self._create_product_precision()
        sale = self._create_sale_order_precision()
        sale.action_confirm()
        for line in sale.order_line:
            line.qty_delivered = line.product_uom_qty
        invoice = sale._create_invoices()

        # invoice._post()
        taxes = invoice._get_taxes_summary()
        self.assertDictEqual(
            taxes,
            {
                "apb": [
                    {
                        "rate": "1.92",
                        "base_amount": "234.86\xa0€",
                        "tax_amount": "1.92\xa0€",
                    }
                ],
                "antibiotics": [],
                "apb_total_tax_amount": "1.92 €",
                "apb_total": 1.92,
                "antibiotics_total_tax_amount": "0.00 €",
                "antibiotics_total": 0,
                "invoice": [
                    {
                        "rate": "6.00",
                        "base_amount": "234.86 €",
                        "tax_amount": "14.09 €",
                    },
                    {"rate": "21.00", "base_amount": "2.00 €", "tax_amount": "0.42 €"},
                ],
                "invoice_total_tax_amount": "14.51 €",
                "invoice_total": 14.511600000000003,
                "contribution_total": 0.0,
                "contribution_total_tax_amount": "0.00 €",
                "amount_without_discount": "273.15 €",
                "amount_untaxed_with_contribution": "236.86 €",
            },
        )

        # Check invoice printing
        # Remove group to have the correct invoice report (without payments)
        group = self.env.ref("account.group_account_invoice")
        self.env.user.groups_id -= group
        report = invoice.action_invoice_print()

        _content, _content_type = self.env["ir.actions.report"]._render_qweb_pdf(
            report.get("report_name"), invoice.ids, False
        )
