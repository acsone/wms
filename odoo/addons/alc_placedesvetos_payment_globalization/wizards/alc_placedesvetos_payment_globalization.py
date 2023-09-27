# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.account_payment_mode.models.account_payment_mode import (
    AccountPaymentMode,
)
from odoo.addons.alc_account_payment_globalization.wizards.alc_account_payment_globalization import (
    AlcAccountPaymentGlobalization,
)
from odoo.addons.base.models.res_partner import Partner


class AlcPlaceDesVetosPaymentGlobalization(AlcAccountPaymentGlobalization):

    _name = "alc.placedesvetos.payment.globalization"
    _description = "alc placedesvetos payment globalization"

    partner_id = fields.Many2one[Partner](
        default=lambda a: a.env.ref("alc_placedesvetos.res_partner_placedesvetos").id
    )

    payment_mode_id = fields.Many2one[AccountPaymentMode](
        default=lambda a: a.env.ref(
            "alc_placedesvetos.account_payment_mode_placedesvetos"
        ).id
    )

    def _after_globalization(self, account_move):
        result = super()._after_globalization(account_move)
        self.env["ir.actions.report"]._render_csv(
            "alc_placedesvetos_report_csv_facpied", account_move.ids, {}
        )
        return result
