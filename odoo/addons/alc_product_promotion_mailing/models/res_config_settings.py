# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.res_config_settings import (
    ResConfigSettings as SaleSettings,
)


class ResConfigSettings(SaleSettings):

    nbr_before_end_promotion_mailing_setting = fields.Integer(
        "Nbr days before end promotion mailing",
        default=3,
        help="Number of days before the end of promotions at which mailings must "
        "be sent to the customer to remind them of the products for which "
        "they have subscribed and whose promotion period is expiring.",
        config_parameter="alc_product_promotion_mailing.nbr_before_end_promotion_mailing_setting",
    )
    promotion_mailing_email_from_setting = fields.Char(
        "Email from address used for the mailing",
        default="secretariat@alcyonbelux.be",
        config_parameter="alc_product_promotion_mailing.promotion_mailing_email_from_setting",
    )
    promotion_website_url_setting = fields.Char(
        "Website URL",
        default="https://www.alcyonbelux.be",
        config_parameter="alc_product_promotion_mailing.promotion_website_url_setting",
    )
