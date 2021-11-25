# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    esb_exported = fields.Boolean(copy=False)

    partner_type_esb_ref = fields.Char(compute="_compute_partner_type_esb_ref")

    @property
    def newpharma_refs(self):
        return ("8114", "8264")

    @api.multi
    def unlink(self):
        for record in self:
            if record.esb_exported:
                raise exceptions.UserError(
                    _(
                        u"The customer {} has already been exported, it can be "
                        u"archived  but not deleted."
                    ).format(record.name)
                )
            return super(ResPartner, self).unlink()

    @api.model
    def partner_type_esb_ref_mapping(self):
        return {
            "veterinary": "01 - Vétérinaires",
            "wholesaler_pharmacy": "02 - Pharmacies",
            "wholesaler_veterinary": "04 - Pharmaciens répartiteurs",
            "export_customer": "11 - Exportation",
            "student_like": "20 - Etudiants",
            "shareholder": "21 - Alcyonnaire",
            "export_meds": "22 - Médicament export",
            "equipment_only": "23 - Exclusif matériel",
            "supplier": "98 - Fournisseurs",
        }

    def _compute_partner_type_esb_ref(self):
        mapping = self.partner_type_esb_ref_mapping()
        for partner in self:
            partner.partner_type_esb_ref = mapping.get(partner.partner_type, "")
