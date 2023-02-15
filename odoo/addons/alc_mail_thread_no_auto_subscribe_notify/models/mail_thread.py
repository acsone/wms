# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mail.models.mail_thread import MailThread as MailThreadBase


class MailThread(MailThreadBase):
    def _message_auto_subscribe_notify(self, partner_ids, template):
        # never send "you have been assigned to" to new followers
        return
