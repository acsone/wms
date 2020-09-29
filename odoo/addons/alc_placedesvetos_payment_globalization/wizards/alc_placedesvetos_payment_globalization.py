# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AlcPlaceDesVetosPaymentGlobalization(models.TransientModel):

    _name = "alc.placedesvetos.payment.globalization"
    _inherit = "alc.account.payment.globalization"

    partner_id = fields.Many2one(
        default=lambda a: a.env.ref("alc_placedesvetos.res_partner_placedesvetos").id
    )

    payment_mode_id = fields.Many2one(
        default=lambda a: a.env.ref(
            "alc_placedesvetos.account_payment_mode_placedesvetos"
        ).id
    )

    def _after_globalization(self, account_move):
        result = super(AlcPlaceDesVetosPaymentGlobalization, self)._after_globalization(
            account_move
        )
        self.env["report"].get_csv(
            account_move.ids, "alc_placedesvetos_report_csv_facpied", {}
        )
        return result
