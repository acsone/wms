# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.models import res_partner


class ResPartner(res_partner.Partner):
    @property
    def newpharma_refs(self):
        return ("8114", "8264")
