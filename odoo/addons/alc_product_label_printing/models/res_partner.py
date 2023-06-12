# © 2017 Sylvain Van Hoof (Okia SPRL)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.alc_label_printing_base.models.res_partner import ResPartner as Partner


class ResPartner(Partner):
    no_labels_products = fields.Boolean(
        string="Do not print product labels",
        help="Customer does not need product labels",
    )
    no_labels_food_products = fields.Boolean(
        string="Do not print food product labels",
        help="Customer does not need product labels.",
    )
