# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    pdf_file = fields.Binary("PDF")

    promo_bag = fields.Boolean("Promo bag?")
    sterile = fields.Boolean("Sterile?")
    fabric = fields.Boolean("Fabric?")

    description_shop_short = fields.Text("Shop short description", translate=True)
    description_shop_long = fields.Text("Shop long description", translate=True)

    class_amcra = fields.Selection(
        string="AMCRA classification",
        selection=[("yellow", "Yellow"), ("orange", "Orange"), ("red", "Red")],
    )

    size_clothing_option_id = fields.Many2one("attribute.option", "Clothing size")
    thread_option_id = fields.Many2one("attribute.option", "Thread")
    food_range_option_id = fields.Many2one("attribute.option", "Food range")
    presentation_option_id = fields.Many2one("attribute.option", "Presentation")

    product_color_option_ids = fields.Many2many(
        string="Colours",
        comodel_name="attribute.option",
        relation="product_template_color_options_rel",
    )
    categ_age_option_ids = fields.Many2many(
        string="Age categories",
        comodel_name="attribute.option",
        relation="product_template_age_options_rel",
    )
    indication_option_ids = fields.Many2many(
        string="Indications",
        comodel_name="attribute.option",
        relation="product_template_indication_options_rel",
    )
    active_principle_option_ids = fields.Many2many(
        string="Active Principles",
        comodel_name="attribute.option",
        relation="product_template_active_principle_options_rel",
    )
    animal_size_option_ids = fields.Many2many(
        string="Animal Sizes",
        comodel_name="attribute.option",
        relation="product_template_animal_size_options_rel",
    )
    administration_route_option_ids = fields.Many2many(
        string="Administration Routes",
        comodel_name="attribute.option",
        relation="product_template_administration_route_options_rel",
    )
