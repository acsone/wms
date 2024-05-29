# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.account.models.account_tax import AccountTax
from odoo.addons.alc_report_base.models.alc_report_print_async import (
    AlcReportPrintAsync,
)
from odoo.addons.alc_sale_consignment.models.sale_order import SaleOrder as Order
from odoo.addons.alc_sale_consignment.models.sale_order_line import (
    SaleOrderLine as OrderLine,
)


class SaleOrderLine(OrderLine):

    only_tax_ids = fields.Many2many[AccountTax](compute="_compute_all_taxes")
    contribution_ids = fields.Many2many[AccountTax](compute="_compute_all_taxes")
    apb_ids = fields.Many2many[AccountTax](compute="_compute_all_taxes")
    amount_contribution = fields.Monetary(compute="_compute_all_taxes")

    @api.depends("tax_id")
    def _compute_all_taxes(self):
        tax_group_apb = self.env.ref("l10n_be_apb_tax.tax_group_apb")

        for line in self:
            amount_contribution = 0
            only_tax_ids = self.env["account.tax"]
            contribution_ids = self.env["account.tax"]
            apb_ids = self.env["account.tax"]

            for tax in line.tax_id:
                if tax.include_base_amount:
                    amount_contribution += tax.amount * line.qty_delivered
                    contribution_ids |= tax
                elif tax.tax_group_id == tax_group_apb:
                    apb_ids |= tax
                else:
                    only_tax_ids |= tax

            line.only_tax_ids = only_tax_ids
            line.contribution_ids = contribution_ids
            line.apb_ids = apb_ids
            line.amount_contribution = amount_contribution

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        # Remove warnings from the invoice line description. Just keep the product name
        res["name"] = self.product_id.name
        return res


class SaleOrder(Order, AlcReportPrintAsync):
    _name = "sale.order"

    def has_human_drug(self):
        """Return if there is at least one line in the sale order.

        with human drugs. Lines with qty at 0 don't count.
        """
        self.ensure_one()
        for line in self.order_line:
            if line.product_id.is_human and line.product_uom_qty > 0:
                return True
        return False

    def order_lines_human_drug(self):
        """Returns this order lines filtered by category human drug."""
        self.ensure_one()
        return self.order_line.filtered("product_id.is_human")

    def get_report_name(self):
        """Generate a specific name for the report save in ir.attachment."""
        self.ensure_one()
        if self.state not in ["sale", "done"]:
            # Not saving the report in ir.attachment, when not confirmed
            return None
        if not self.partner_id.ref:
            raise UserError(
                _(
                    "The Quotation can not be printed the client %(partner_name)s "
                    "(%(partner_id)s) has no reference assigned.",
                    partner_name=self.partner_id.name,
                    partner_id=self.partner_id.id,
                )
            )
        return (
            "_".join(
                [
                    "cf",
                    self.partner_id.ref,
                    str(self.id),
                    self.create_date.strftime("%Y%m%d_%H%M%S"),
                ]
            )
            + ".pdf"
        )

    def create_reports(self):
        """Create the jobs to create base sale order PDF and send them.

        according to sale_channel
        """
        for order in self:
            order.with_delay(priority=4).print_and_attach_report(
                "sale.report_saleorder",
                order.partner_id.fax if order.sale_channel_id.name == "fax" else None,
            )

    def _get_pharmacist(self, raise_errors=True):
        """Get the pharmacist to which we will send emails."""
        pharmacist = self.partner_id.pharmacist_id
        if raise_errors:
            if not pharmacist:
                raise UserError(
                    _(
                        "Cannot send pharmacist email\n"
                        "No pharmacist affiliated to the client."
                    )
                )
            if not pharmacist.email:
                raise UserError(
                    _(
                        "Cannot send pharmacist email\n"
                        "%(pharmacist)s partner must have an email address.",
                        pharmacist=pharmacist.name,
                    )
                )
        return pharmacist

    def force_pharmacist_email_send(self, pharmacist):
        template_xid = "alc_report_sale.email_template_pharmacist_supplier_order"
        mail_template = self.env.ref(template_xid)
        if not pharmacist:
            pharmacist = self._get_pharmacist()
        for order in self:
            mail_template.lang = pharmacist.lang
            mail_template.send_mail(
                res_id=order.id,
                force_send=True,
                email_layout_xmlid="mail.mail_notification_layout",
                email_values={"email_to": pharmacist.email},
            )
            mail_template.lang = order.partner_id.lang
            order.with_context(mark_so_as_sent=False).message_post_with_template(
                template_id=mail_template.id,
                composition_mode="comment",
            )
        return True

    def create_pharmacist_reports(self):
        """Create the jobs to forward ordered human drugs to the pharmacist."""
        pharmacist = None
        for order in self:
            if order.has_human_drug():
                # Try to fetch pharmacist only if there is at least
                # one order with human drugs
                if not pharmacist:
                    pharmacist = self._get_pharmacist()
                order.force_pharmacist_email_send(pharmacist)

    def action_confirm(self):
        """Generate the sale order pdf and save it in ir.attachment."""
        res = super().action_confirm()
        confirmed_orders = self.filtered(lambda o: o.state in ("sale", "done"))
        # if config["test_enable"] or self.env.context.get("skip_pdf_gen"):
        #     # Do not generate the report during test or during import
        #     return res
        if self.env["ir.config_parameter"].sudo().get_param(
            "alc_report_sale.on_confirm_generate_quotation_report", ""
        ).lower() in ["true", "1", "t", "y", "yes"]:
            confirmed_orders.create_reports()
        if self.env["ir.config_parameter"].sudo().get_param(
            "alc_report_sale.on_confirm_generate_and_send_pharmacist_report",
            "",
        ).lower() in ["true", "1", "t", "y", "yes"]:
            confirmed_orders.create_pharmacist_reports()
        return res

    def print_quotation(self):
        """Only keep one sale order with the same name in ir.attachment."""
        res = super().print_quotation()
        for so in self:
            filename = so.get_report_name()
            existing = self.env["ir.attachment"].search(
                [("name", "=", filename), ("res_model", "=", "sale.order")]
            )
            existing.unlink()
        return res
