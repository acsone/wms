# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    def _get_outstanding_info_JSON(self):
        result = super(AccountInvoice, self)._get_outstanding_info_JSON()
        info = json.loads(self.outstanding_credits_debits_widget)
        if info and "content" in info.keys() and info["content"]:
            content = info["content"]
            line_ids = [el["id"] for el in content]
            lines = self.env["account.move.line"].browse(line_ids)
            line_ids_to_keep = lines.filtered(
                lambda l: l.payment_mode_id == self.payment_mode_id
            ).ids
            result = [el for el in content if el["id"] in line_ids_to_keep]
            if result:
                info["content"] = result
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True
            else:
                self.outstanding_credits_debits_widget = json.dumps(False)
                self.has_outstanding = False
        return result
