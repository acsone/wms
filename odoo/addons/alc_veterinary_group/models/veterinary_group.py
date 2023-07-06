# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VeterinaryGroup(models.Model):

    _name = "veterinary.group"
    _description = "Veterinary Group"
    _order = "sequence"

    name = fields.Char(string="Name")
    is_alcyonnaire = fields.Boolean()
    display_color = fields.Char(
        "Color", oldname="color"
    )  # field name 'color' is reserved for m2mtags widget
    sequence = fields.Integer(default=-1, required=True)
    partner_ids = fields.Many2many(
        "res.partner",
        "res_partner_veterinary_group_rel",
        "veterinary_group_id",
        "res_partner_id",
        string="Partners",
    )
    product_template_ids = fields.Many2many(
        "product.template",
        "product_template_veterinary_group_rel",
        "veterinary_group_id",
        "product_template_id",
        string="Products",
    )

    def write(self, vals):
        if "partner_ids" in vals:
            partners_alcyonnaire = self.mapped("partner_ids").filtered(
                lambda p: p.is_alcyonnaire
            )
        res = super(VeterinaryGroup, self).write(vals)
        if "partner_ids" in vals:
            partners_no_more_alcyonnaire = partners_alcyonnaire - self.mapped(
                "partner_ids"
            ).filtered(lambda p: p.is_alcyonnaire)
            partners_no_more_alcyonnaire._check_date_end_contract_alcyonnaire()
        return res
