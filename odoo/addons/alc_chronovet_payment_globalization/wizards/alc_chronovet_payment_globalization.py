# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AlcChronovetPaymentGlobalization(models.TransientModel):

    _name = "alc.chronovet.payment.globalization"
    _inherit = "alc.account.payment.globalization"

    partner_id = fields.Many2one(
        default=lambda a: a.env.ref("alc_chronovet.res_partner_chronovet").id
    )

    payment_mode_id = fields.Many2one(
        default=lambda a: a.env.ref("alc_chronovet.account_payment_mode_chronovet").id
    )

    def _after_globalization(self, account_move):
        result = super(AlcChronovetPaymentGlobalization, self)._after_globalization(
            account_move
        )
        self.env["report"].get_csv(
            account_move.ids, "alc_chronovet_report_csv_facpied", {}
        )
        self.env["report"].get_csv(
            account_move.ids, "alc_chronovet_report_csv_faclign", {}
        )
        return result
