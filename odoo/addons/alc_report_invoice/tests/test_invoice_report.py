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

        cls.sale_obj = cls.env["sale.order"]
        cls.product_obj = cls.env["product.product"]
        cls.apb_group = cls.env.ref("l10n_be_apb_tax.tax_group_apb")
        cls.sale_group = cls.env.ref("l10n_be.tax_group_tva_21")
        tax_21 = cls.env["account.tax"].search(
            [
                ("type_tax_use", "=", "sale"),
                ("tax_group_id", "=", cls.sale_group.id),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        taxes_apb = cls.env["account.tax"].search(
            [
                ("tax_group_id", "=", cls.apb_group.id),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
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
        cls.product_1.taxes_id = tax_21 | taxes_apb
        cls.product_2 = cls.product_obj.create(
            {"name": "Product 2", "type": "service", "service_type": "manual"}
        )
        cls.product_2.taxes_id = tax_21

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
                "invoice": [
                    {"base_amount": "20.00 €", "rate": "21.00", "tax_amount": "4.20 €"}
                ],
                "invoice_total_tax_amount": "4.20 €",
                "invoice_total": 4.2,
                "apb": [
                    {"base_amount": "10.00 €", "rate": "0.02", "tax_amount": "0.22 €"}
                ],
                "apb_total_tax_amount": "0.22 €",
                "apb_total": 0.22,
                "antibiotics": [],
                "antibiotics_total_tax_amount": "0.00 €",
                "antibiotics_total": 0,
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
                "invoice": [
                    {"base_amount": "20.00 €", "rate": "21.00", "tax_amount": "4.20 €"}
                ],
                "invoice_total_tax_amount": "4.20 €",
                "invoice_total": 4.2,
                "apb": [
                    {"base_amount": "10.00 €", "rate": "0.02", "tax_amount": "0.22 €"}
                ],
                "apb_total_tax_amount": "0.22 €",
                "apb_total": 0.22,
                "antibiotics": [],
                "antibiotics_total_tax_amount": "0.00 €",
                "antibiotics_total": 0,
                "contribution_total": 0.0,
                "contribution_total_tax_amount": "0.00 €",
                "amount_without_discount": "20.00 €",
                "amount_untaxed_with_contribution": "20.00 €",
            },
        )
