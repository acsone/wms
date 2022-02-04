# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleConfigSettings(models.TransientModel):

    _inherit = "sale.config.settings"

    nbr_before_end_promotion_mailing_setting = fields.Integer(
        "Nbr days before end promotion mailing",
        default=3,
        help="Number of days before the end of promotions at which mailings must "
        "be sent to the customer to remind them of the products for which "
        "they have subscribed and whose promotion period is expiring.",
    )
    promotion_mailing_email_from_setting = fields.Char(
        "Email from address used for the mailing", default="secretariat@alcyonbelux.be",
    )

    @api.multi
    def set_nbr_before_end_promotion_mailing_defaults(self):
        return (
            self.env["ir.values"]
            .sudo()
            .set_default(
                "sale.config.settings",
                "nbr_before_end_promotion_mailing_setting",
                self.nbr_before_end_promotion_mailing_setting,
            )
        )

    @api.multi
    def set_promotion_mailing_email_from_defaults(self):
        return (
            self.env["ir.values"]
            .sudo()
            .set_default(
                "sale.config.settings",
                "promotion_mailing_email_from_setting",
                self.promotion_mailing_email_from_setting,
            )
        )

    @api.model
    def get_nbr_before_end_promotion_mailing(self):
        return (
            self.env["ir.values"]
            .get_defaults_dict("sale.config.settings")
            .get("nbr_before_end_promotion_mailing_setting", 3)
        )

    @api.model
    def get_promotion_mailing_email_from(self):
        return (
            self.env["ir.values"]
            .get_defaults_dict("sale.config.settings")
            .get("promotion_mailing_email_from_setting", "secretariat@alcyonbelux.be",)
        )
