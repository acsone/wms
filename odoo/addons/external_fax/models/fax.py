# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
import re

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import UserError


class Fax(models.Model):
    _name = 'fax.external'

    name = fields.Char(string='Fax name')
    email_from = fields.Char(string='Email from', compute='_compute_from_env')
    email_domain = fields.Char(
        string='Email domain of the service', compute='_compute_from_env'
    )
    fax_number = fields.Char(
        string='Fax number of the service', compute='_compute_from_env'
    )
    password = fields.Char(
        string='Password of the service', compute='_compute_from_env'
    )

    @api.depends()
    def _compute_from_env(self):
        for record in self:
            record.email_from = os.getenv('OVH_FAX_EMAIL_FROM', '')
            record.email_domain = os.getenv('OVH_FAX_EMAIL_DOMAIN', '')
            record.fax_number = os.getenv('OVH_FAX_NUMBER', '')
            record.password = os.getenv('OVH_FAX_PASSWORD', '')

    @api.multi
    def email_recipient(self, recipient_fax_number):
        """ Generate the email recipient.

        It is build like this
        {fax number of the recipient} @ {email domain}
        All non-digit char are striped from the number.
        """
        self.ensure_one()
        fax_no = re.sub('[^0-9]', '', recipient_fax_number)
        email_recipient = ''.join([fax_no, '@', self.email_domain])
        return email_recipient

    @api.multi
    def subject(self):
        """The subject is the fax number of the service."""
        self.ensure_one()
        return self.fax_number

    @api.multi
    def body(self):
        """ The password to the service is sent in the body of the message."""
        self.ensure_one()
        return u'password:{}'.format(self.password)

    @api.multi
    @job(default_channel='root.background.fax')  # priority=10
    def send(self, fax_no, attachment_id):
        """Send an email to the fax service

        The file referenced by the attachment_id is send to the number fax_no.
        """
        self.ensure_one()
        if not fax_no:
            raise UserError(
                _(
                    u'Fax could not be sent for attachment with '
                    u'id {}. Fax number is empty or invalid.'
                ).format(attachment_id)
            )
        mail_values = {
            'email_to': self.email_recipient(fax_no),
            'body_html': self.body(),
            'auto_delete': False,
        }
        email_from = self.email_from
        if email_from:
            mail_values['email_from'] = email_from
        new_mail = self.env['mail.mail'].create(mail_values)
        new_mail.mail_message_id.attachment_ids = [(4, attachment_id, False)]
        new_mail.mail_message_id.subject = self.fax_number
        new_mail.send()
        return new_mail
