# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AlcEshopForm(models.Model):

    _name = "alc.eshop.form"
    _description = "Eshop Form"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    audience = fields.Selection(
        selection=[("public_only", "Public"), ("authenticated_only", "Authenticated")],
        required=True,
    )
    form = fields.Text(required=True)
    form_options = fields.Text(
        required=True, default=lambda a: a._get_default_form_options()
    )
    email = fields.Char(required=True)
    email_subject = fields.Char(required=True)
    log_on_partner = fields.Boolean(
        help="If checked, each time a partner submit a form, a comment will "
        "be added into the partner's chatter",
        default=True,
    )
    published = fields.Boolean("Visible on EShop", copy=False, default=False)
    code = fields.Char(required=True, translate=False)
    sequence = fields.Integer(default=-1, required=True)

    _sql_constraints = [("code_uniq", "unique(code)", "The code must be unique!")]

    def publish_button(self):
        for rec in self:
            rec.published = not rec.published

    @api.constrains("form_options")
    def _check_form_options(self):
        for record in self:
            try:
                json.loads(record.form_options)
            except ValueError:
                raise ValidationError(_("Options are not a json valid string"))

    @api.constrains("form")
    def _check_form(self):
        for record in self:
            try:
                json.loads(record.form)
            except ValueError:
                raise ValidationError(_("Form is not a json valid string"))

    @property
    def _default_form_options(self):
        return {"i18n": {"fr": {}, "en": {}, "nl": {}}}

    @api.model
    def _get_default_form_options(self):
        return json.dumps(self._default_form_options, indent=True, sort_keys=True)

    @api.model
    def _get_default_code_from_vals(self, vals):
        name = vals["name"]
        audience = vals["audience"]
        return "_".join((name[:3].upper(), audience[:3].upper()))

    @api.model
    def create(self, vals):
        if not vals.get("code"):
            vals["code"] = self._get_default_code_from_vals(vals)
        return super(AlcEshopForm, self).create(vals)

    def _send_collected_info(self, info, partner=None):
        """ send an email with the collected info from the form submission

        info is a dict of ('name' : 'value') info submitted. If the form
        has been submitted by an authenticated partner, the partner is filled

        """
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url").rstrip("/")
        partner_form_url = ""
        if partner:
            partner_form_url = "{}/web#id={}&view_type=form&model=res.partner".format(
                base_url, partner.id,
            )
        data = {
            "info": info,
            "partner": partner,
            "company": self.env.user.company_id,
            "eshop_form": self,
            "partner_form_url": partner_form_url,
            "base_url": base_url,
        }
        html = self.env["report"].get_html(
            docids=None, report_name="report_alc_eshop_form_submission", data=data,
        )
        mail_values = {
            "email_to": self.email,
            "body_html": html,
            "auto_delete": False,
            "email_from": "eshop@alcyonbelux.be",
        }
        if partner and self.log_on_partner:
            # add the message into the mail thread of the given partner
            partner.message_post(
                body=html, subject=self.email_subject, message_type="notification",
            )
        new_mail = self.env["mail.mail"].create(mail_values)
        new_mail.mail_message_id.subject = self.email_subject
        new_mail.send()
        return new_mail
