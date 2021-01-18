# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    only_tax_ids = fields.Many2many("account.tax", compute="_compute_all_taxes")
    contribution_ids = fields.Many2many("account.tax", compute="_compute_all_taxes")
    apb_ids = fields.Many2many("account.tax", compute="_compute_all_taxes")
    amount_contribution = fields.Monetary(compute="_compute_all_taxes")

    @api.multi
    @api.depends("tax_id")
    def _compute_all_taxes(self):
        tax_group_apb = self.env.ref("specific_account.tax_group_apb")

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


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "report.async"]

    @api.multi
    def has_human_drug(self):
        """ Return if there is at least one line in the sale order
        with human drugs. Lines with qty at 0 don't count.
        """
        self.ensure_one()
        categ = self.env.ref("specific_data.product_categ_humain")
        for line in self.order_line:
            if line.product_id.categ_id == categ and line.product_uom_qty > 0:
                return True
        return False

    @api.multi
    def order_lines_human_drug(self):
        """
        Returns this order lines filtered by category human drug.

        """
        self.ensure_one()
        categ = self.env.ref("specific_data.product_categ_humain")
        lines = self.order_line
        return lines.filtered(lambda rec: rec.product_id.categ_id == categ)

    @api.multi
    def get_report_name(self):
        """Generate a specific name for the report save in ir.attachment"""
        self.ensure_one()
        if self.state not in ["sale", "done"]:
            # Not saving the report in ir.attachment, when not confirmed
            return None
        if not self.partner_id.ref:
            raise UserError(
                _(
                    u"The Quotation can not be printed the client {} ({}) "
                    u"has no reference assigned."
                ).format(self.partner_id.name, self.partner_id.id)
            )
        return (
            u"_".join(
                [
                    "cf",
                    self.partner_id.ref,
                    str(self.id),
                    "".join(self.create_date[:10].split("-")),
                    "".join(self.create_date[-8:].split(":")),
                ]
            )
            + ".pdf"
        )

    @api.multi
    def create_reports(self):
        """Create the jobs to create base sale order PDF and send them
        according to sale_channel
        """
        for order in self:
            order.with_delay(priority=4).print_and_attach_report(
                "sale.report_saleorder",
                order.partner_id.fax if order.sale_channel == "fax" else None,
            )

    @api.multi
    def _get_pharmacist(self, raise_errors=True):
        """Get the pharmacist to which we will send emails"""
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
                        "%s partner must have an email address."
                    )
                    % pharmacist.name
                )
        return pharmacist

    @api.multi
    def action_send_pharmacist_email(self, pharmacist=None):
        """ This action is not available on front.

        Based on `action_quotation_send`
        """
        template_xid = "specific_report.email_template_pharmacist_supplier_order"
        mail_template = self.env.ref(template_xid)
        if not pharmacist:
            pharmacist = self._get_pharmacist()
        ctx = {
            "default_email_to": pharmacist and pharmacist.email,
            "default_partner_ids": [],
            "default_model": "sale.order",
            "default_res_id": self.ids[0],
            "default_use_template": bool(mail_template),
            "default_template_id": mail_template.id,
            "default_composition_mode": "comment",
            "mark_so_as_sent": False,
            "custom_layout": ("specific_sale" ".mail_template_pharamcist_notification"),
        }
        try:
            wiz_xid = "mail.email_compose_message_wizard_form"
            compose_form_id = self.env.ref(wiz_xid)
        except ValueError:
            compose_form_id = False
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    @api.multi
    def force_pharmacist_email_send(self, pharmacist):
        for order in self:
            email_act = order.action_send_pharmacist_email(pharmacist)
            if email_act and email_act.get("context"):
                email_ctx = email_act["context"]
                email_ctx.update(default_email_from=order.company_id.email)

                # FIXME separate chatter and email sending
                order.with_context(email_ctx).message_post_with_template(
                    email_ctx.get("default_template_id")
                )
        return True

    @api.multi
    def create_pharmacist_reports(self):
        """Create the jobs to forward ordered human drugs to the pharmacist.

        """
        pharmacist = None
        for order in self:
            if order.has_human_drug():
                # Try to fetch pharmacist only if there is at least
                # one order with human drugs
                if not pharmacist:
                    pharmacist = self._get_pharmacist()
                order.force_pharmacist_email_send(pharmacist)

    @api.multi
    def action_confirm(self):
        """ Generate the sale order pdf and save it in ir.attachment"""
        res = super(SaleOrder, self).action_confirm()
        if config["test_enable"] or self.env.context.get("skip_pdf_gen"):
            # Do not generate the report during test or during import
            return res
        self.create_reports()
        self.create_pharmacist_reports()
        return res

    @api.multi
    def print_quotation(self):
        """Only keep one sale order with the same name in ir.attachment"""
        res = super(SaleOrder, self).print_quotation()
        for so in self:
            filename = so.get_report_name()
            existing = self.env["ir.attachment"].search(
                [("name", "=", filename), ("res_model", "=", "sale.order")]
            )
            existing.unlink()
        return res
