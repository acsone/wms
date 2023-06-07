# © 2017 Sylvain Van Hoof (Okia SPRL)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    is_price_on_labels = fields.Boolean("Display price on labels")
