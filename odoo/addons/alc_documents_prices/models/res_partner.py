# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.jobify_process_dossier()
        return res

    @api.model
    def dossier_watched_fields(self):
        return [
            "supplier_promotion_sale_allowed",
            "discount_pricelist_id",
            "property_product_pricelist",
        ]

    def write(self, vals):
        res = super().write(vals)
        if any(field in vals for field in self.dossier_watched_fields()):
            self.jobify_process_dossier()
        return res

    def jobify_process_dossier(self):
        for partner in self.filtered("needs_dossier"):
            description = _("Process dossier for partner %(name)s", name=partner.name)
            partner.with_delay(description=description)._process_dossier()

    def _process_dossier(self):
        document_model = self.env["alc.document"]
        for partner in self.filtered("needs_dossier"):
            # we remove everything, so it 'invalidates the cache'
            # thus we don't need to check values before/after etc
            domain = [
                ("partner_id", "=", partner.id),
                ("compute", "in", ["discount", "pricelist"]),
            ]
            to_remove = document_model.search(domain)
            to_remove.mapped("attachment_id").unlink()
            to_remove.sudo().unlink()
            document_model._create_pricelist(partner)
            if partner.supplier_promotion_sale_allowed:
                document_model._create_discount(partner)
