# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.product.models.product_template import ProductTemplate


class VeterinaryGroup(models.Model):

    _name = "veterinary.group"
    _description = "Veterinary Group"
    _order = "sequence"

    name = fields.Char(string="Name")
    is_alcyonnaire = fields.Boolean()
    display_color = fields.Char("Color")
    sequence = fields.Integer(default=-1, required=True)
    partner_ids = fields.Many2many[Partner](
        relation="res_partner_veterinary_group_rel",
        column1="veterinary_group_id",
        column2="res_partner_id",
        string="Partners",
    )
    product_template_ids = fields.Many2many[ProductTemplate](
        relation="product_template_veterinary_group_rel",
        column1="veterinary_group_id",
        column2="product_template_id",
        string="Products",
    )

    def write(self, vals):
        if "partner_ids" in vals:
            partners_alcyonnaire = self.partner_ids.filtered(lambda p: p.is_alcyonnaire)
        res = super().write(vals)
        if "partner_ids" in vals:
            partners_no_more_alcyonnaire = (
                partners_alcyonnaire
                - self.partner_ids.filtered(lambda p: p.is_alcyonnaire)
            )
            partners_no_more_alcyonnaire._check_date_end_contract_alcyonnaire()
        return res
