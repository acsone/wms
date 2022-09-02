# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import inspect
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LazyDeliveryPersonIdContext(object):
    def __call__(self, source):
        context = {
            "default_customer": False,
            "default_is_delivery_person": True,
            "search_default_is_delivery_person": 1,
        }
        try:
            frame = inspect.currentframe()
            if frame is None:
                return None
            # the previous frame is the one from the access to the attribute
            # into the field Object
            frame = frame.f_back
            if not frame:
                return None
            env = frame.f_locals.get("env")

            if env:
                context["default_category_id"] = [
                    (
                        4,
                        env.ref(
                            "alc_partner_delivery_person.res_partner_category_delivery_person"
                        ).id,
                    )
                ]
        except Exception:
            _logger.exception(
                'Not able to build field context for "%r", skipped', source
            )
        return repr(context)


class AlcDeliveryResource(models.Model):

    _name = "alc.delivery.resource"
    _description = "Alc Delivery Resource"
    _order = "delivery_person_id ASC"
    _rec_name = "name"

    geo_optimization_resource_id = fields.Selection(
        selection="_selection_geo_optimization_resource_id", required=True
    )
    delivery_person_id = fields.Many2one(
        comodel_name="res.partner",
        string="Delivery person's contact information",
        domain=[("is_delivery_person", "=", True)],
        context=LazyDeliveryPersonIdContext(),
    )
    use_delivery_person_coordinates_as_end = fields.Boolean(
        help="If true the computed delivery will end at the delivery person's "
        "address. Otherwise it will end at the Alcyon warehouse"
    )

    name = fields.Char(compute="_compute_name", store=True)

    _sql_constraints = [
        (
            "resource_uniq_id",
            "UNIQUE(geo_optimization_resource_id)",
            _("Resource ID must be unique"),
        )
    ]

    @api.depends("geo_optimization_resource_id", "delivery_person_id")
    def _compute_name(self):
        for record in self:
            name = record.geo_optimization_resource_id
            if record.delivery_person_id:
                name = u"{} ({})".format(name, record.delivery_person_id.display_name,)
            record.name = name

    @api.model
    def get_optimization_config(self):
        return self.env["stock.config.settings"].get_optimization_config()

    @api.model
    def _selection_geo_optimization_resource_id(self):
        resource_number = self.get_optimization_config().resources_number
        return [("D%d" % (i + 1), "D%d" % (i + 1)) for i in range(resource_number)]

    @api.constrains("use_delivery_person_coordinates_as_end", "delivery_person_id")
    def _check_use_person_coodinates_as_end(self):
        for rec in self:
            if (
                rec.use_delivery_person_coordinates_as_end
                and not rec.delivery_person_id.partner_longitude
            ):
                raise ValidationError(
                    _(
                        "A delivery person with a geolocalized address is required "
                        "if you want to end the delivey round at the delivery person's "
                        "address."
                    )
                )
