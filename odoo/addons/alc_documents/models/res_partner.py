# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):
    _inherit = "res.partner"

    needs_dossier = fields.Boolean(compute="_compute_needs_dossier")

    alc_document_count = fields.Integer(
        compute="_compute_alc_document_count",
        string="# of documents",
    )

    def _compute_alc_document_count(self):
        document_model = self.env["alc.document"]
        for partner in self:
            domain_partner = document_model.get_partner_domain(partner)
            partner.alc_document_count = len(document_model.search(domain_partner))

    @api.depends("is_b2c_customer")
    def _compute_needs_dossier(self):
        for partner in self:
            partner.needs_dossier = not partner.is_b2c_customer

    def action_show_documents(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Documents"),
            "res_model": "alc.document",
            "domain": self.env["alc.document"].get_partner_domain(self),
            "view_type": "form",
            "view_mode": "tree,form",
            "context": self.env.context,
            "target": "current",
        }
