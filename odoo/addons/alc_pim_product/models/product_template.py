# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import inspect
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LazyDefaultAttributeIdContext(object):
    def __call__(self, source):
        try:
            frame = inspect.currentframe()
            if frame is None:
                return None
            # the previous frame is the one from the access to the attribute
            # into the field Object
            frame = frame.f_back
            if not frame:
                return None
            field = frame.f_locals.get("self")
            env = frame.f_locals.get("env")
            if field and env:
                attribute_attribute_xmlid = "alc_pim_product.attribute_%s" % field.name
                return "{'default_attribute_id': %s}" % (
                    env.ref(attribute_attribute_xmlid).id
                )
            _logger.Exception("Not able to build field context")
        except Exception:
            _logger.Exception(
                'Not able to build field context for "%r", skipped', source
            )
        return {}


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
        domain=lambda a: a._get_domain("product_color_option_ids"),
        context=LazyDefaultAttributeIdContext(),
    )
    categ_age_option_ids = fields.Many2many(
        string="Age categories",
        comodel_name="attribute.option",
        relation="product_template_age_options_rel",
        domain=lambda a: a._get_domain("categ_age_option_ids"),
        context=LazyDefaultAttributeIdContext(),
    )
    indication_option_ids = fields.Many2many(
        string="Indications",
        comodel_name="attribute.option",
        relation="product_template_indication_options_rel",
        domain=lambda a: a._get_domain("indication_option_ids"),
        context=LazyDefaultAttributeIdContext(),
    )
    active_principle_option_ids = fields.Many2many(
        string="Active Principles",
        comodel_name="attribute.option",
        relation="product_template_active_principle_options_rel",
        domain=lambda a: a._get_domain("active_principle_option_ids"),
        context=LazyDefaultAttributeIdContext(),
    )
    animal_size_option_ids = fields.Many2many(
        string="Animal Sizes",
        comodel_name="attribute.option",
        relation="product_template_animal_size_options_rel",
        domain=lambda a: a._get_domain("animal_size_option_ids"),
        context=LazyDefaultAttributeIdContext(),
    )
    administration_route_option_ids = fields.Many2many(
        string="Administration Routes",
        comodel_name="attribute.option",
        relation="product_template_administration_route_options_rel",
        domain=lambda a: a._get_domain("administration_route_option_ids"),
        context=LazyDefaultAttributeIdContext(),
    )

    @api.model
    def _get_domain(self, fn_name):
        attribute_attribute_xmlid = "alc_pim_product.attribute_%s" % fn_name
        return [("attribute_id", "=", self.env.ref(attribute_attribute_xmlid).id)]
