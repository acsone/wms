# Copyright 2024 ACSONE SA/NV

import re

from odoo import api

from odoo.addons.account_accountant.models.bank_rec_widget import (
    BankRecWidget as BankRecWidgetBase,
)


def _is_bbacomm(val):
    supported_chars = "0-9+*/ "
    pattern = re.compile("[^" + supported_chars + "]")
    if pattern.findall(val or ""):
        return False
    bbacomm = re.sub(r"\D", "", val or "")
    if len(bbacomm) == 12:
        base = int(bbacomm[:10])
        mod = base % 97 or 97
        if mod == int(bbacomm[-2:]):
            return True
    return False


class BankRecWidget(BankRecWidgetBase):
    @api.depends("st_line_id")
    def _compute_amls_widget(self):
        res = super()._compute_amls_widget()
        for wizard in self:
            st_line = wizard.st_line_id
            if _is_bbacomm(st_line.payment_ref):
                wizard.amls_widget["context"][
                    "search_default_name"
                ] = st_line.payment_ref
                wizard.amls_widget["context"]["search_default_partner_id"] = False
        return res

    def _action_trigger_matching_rules(self):
        """If the payment reference is bba com and the matching rules don't find a.

        candidate aml, we rerun the rules without the partner to try to find a matching
        aml from other partners.
        """
        res = super()._action_trigger_matching_rules()
        if not res and _is_bbacomm(self.st_line_id.payment_ref):
            partner = self.partner_id
            self.partner_id = False
            res = super()._action_trigger_matching_rules()
            self.partner_id = partner
            return res
        return res
