# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    pdf_file = fields.Binary("PDF")

    promo_bag = fields.Boolean("Promo bag?")
    sterile = fields.Boolean("Sterile?")
    fabric = fields.Boolean("Fabric?")

    description_shop_short = fields.Html(
        "Shop short description", translate=True, sanitize=False
    )
    description_shop_long = fields.Html(
        "Shop long description", translate=True, sanitize=False
    )

    class_amcra = fields.Selection(
        string="AMCRA classification",
        selection=[("yellow", "Yellow"), ("orange", "Orange"), ("red", "Red")],
    )

    size_clothing_option_id = fields.Many2one(
        "attribute.option",
        "Clothing size",
        domain=lambda a: a._get_domain("size_clothing_option_id"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "size_clothing_option_id"
            )
        },
    )
    thread_option_id = fields.Many2one(
        "attribute.option",
        "Thread",
        domain=lambda a: a._get_domain("thread_option_id"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id("thread_option_id")
        },
    )
    food_range_option_id = fields.Many2one(
        "attribute.option",
        "Food range",
        domain=lambda a: a._get_domain("food_range_option_id"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "food_range_option_id"
            )
        },
    )
    presentation_option_id = fields.Many2one(
        "attribute.option",
        "Presentation",
        domain=lambda a: a._get_domain("presentation_option_id"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "presentation_option_id"
            )
        },
    )
    product_color_option_ids = fields.Many2many(
        string="Colours",
        comodel_name="attribute.option",
        relation="product_template_color_options_rel",
        domain=lambda a: a._get_domain("product_color_option_ids"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "product_color_option_ids"
            )
        },
    )
    categ_age_option_ids = fields.Many2many(
        string="Age categories",
        comodel_name="attribute.option",
        relation="product_template_age_options_rel",
        domain=lambda a: a._get_domain("categ_age_option_ids"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "categ_age_option_ids"
            )
        },
    )
    indication_option_ids = fields.Many2many(
        string="Indications",
        comodel_name="attribute.option",
        relation="product_template_indication_options_rel",
        domain=lambda a: a._get_domain("indication_option_ids"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "indication_option_ids"
            )
        },
    )
    active_principle_option_ids = fields.Many2many(
        string="Active Principles",
        comodel_name="attribute.option",
        relation="product_template_active_principle_options_rel",
        domain=lambda a: a._get_domain("active_principle_option_ids"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "active_principle_option_ids"
            )
        },
    )
    animal_size_option_ids = fields.Many2many(
        string="Animal Sizes",
        comodel_name="attribute.option",
        relation="product_template_animal_size_options_rel",
        domain=lambda a: a._get_domain("animal_size_option_ids"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "animal_size_option_ids"
            )
        },
    )
    administration_route_option_ids = fields.Many2many(
        string="Administration Routes",
        comodel_name="attribute.option",
        relation="product_template_administration_route_options_rel",
        domain=lambda a: a._get_domain("administration_route_option_ids"),
        context={
            "default_attribute_id": lambda a: a._get_attribute_id(
                "administration_route_option_ids"
            )
        },
    )

    @api.model
    def _get_domain(self, fn_name):
        return [("attribute_id", "=", self._get_attribute_id(fn_name))]

    @api.model
    def _get_attribute_id(self, fn_name):
        attribute_attribute_xmlid = f"alc_pim_product.attribute_{fn_name}"
        return self.env.ref(attribute_attribute_xmlid).id
