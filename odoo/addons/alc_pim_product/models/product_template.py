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
        string="Colour", comodel_name="attribute.option"
    )
    categ_age_option_ids = fields.Many2many(
        string="Age category", comodel_name="attribute.option"
    )
    indication_option_ids = fields.Many2many(
        string="Indications", comodel_name="attribute.option"
    )
    active_principle_option_ids = fields.Many2many(
        string="Active Principle", comodel_name="attribute.option"
    )
    animal_size_option_ids = fields.Many2many(
        string="Animal Size", comodel_name="attribute.option"
    )
    administration_route_option_ids = fields.Many2many(
        string="Administration Route", comodel_name="attribute.option"
    )
