# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AlcChronovetBackend(models.Model):

    _name = "alc.chronovet.backend"
    _description = "Chronovet Config"
    _inherit = "connector.backend"

    name = fields.Char()
    product_assortment_id = fields.Many2one(
        string="Product Assortment",
        comodel_name="ir.filters",
        help="Allows only products matching with the assortment domain",
        domain=[("is_assortment", "=", True)],
        context={"product_assortment": True},
    )
    pricelist_id = fields.Many2one(
        "product.pricelist", string="Pricelist", required=True
    )
    sale_team_id = fields.Many2one("crm.team", string="Sale Team", required=True)
    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode",
        domain=[("payment_type", "=", "inbound")],
    )
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")

    @api.model
    def get_singleton(self):
        return self.env.ref("alc_chronovet_connector.alc_chronovet_backend")

    @api.model
    def create(self, vals):
        existing = self.search([])
        if existing:
            raise UserError(_("Only 1 ChronoVet backend configuration is allowed."))
        return super(AlcChronovetBackend, self).create(vals)
