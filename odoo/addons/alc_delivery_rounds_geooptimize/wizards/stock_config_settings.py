# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import namedtuple

from odoo import api, fields, models
from odoo.tools import ormcache

OptimizationConfig = namedtuple(
    "OptimizationConfig",
    "enabled,api_url,api_key,duration,delivery_duration,loading_duration,"
    "resources_number,work_penalty,travel_penalty,daily_work_time",
)


class StockConfigSettings(models.TransientModel):

    _inherit = "stock.config.settings"

    geo_optimization_enabled = fields.Boolean("Optimization activated")
    geo_optimization_api_url = fields.Char("TourSolver API url")
    geo_optimization_api_key = fields.Char("TourSolver API Key")
    geo_optimization_duration = fields.Integer(
        "Optimization process max duration",
        help="Duration in seconds allowed to the computation of " "the optimization",
    )
    geo_optimization_delivery_duration = fields.Integer(
        "Fixed time spent deliverying a customer",
        help="Duration in seconds needed to deliver a cutomer",
    )

    geo_optimization_loading_duration = fields.Integer(
        "Fixed initial loading time", help="Loading time in minutes"
    )
    geo_optimization_resources_number = fields.Integer(
        "Number of available resource",
        help="Resource into geoconcept must be named as D1, D2, ....",
    )
    geo_optimization_work_penalty = fields.Float(
        "Fixed cost working/hour", help="The cost of a resource working for an hour."
    )
    geo_optimization_travel_penalty = fields.Float(
        "Fixed cost travelling/hour",
        help="The cost for a resource of driving for one distance unit.",
    )
    geo_optimization_daily_work_time = fields.Float("Resources Daily Working Hours")

    @api.model
    @ormcache()
    def get_optimization_config(self):
        IrConfigParameter = self.env["ir.config_parameter"]
        enabled = IrConfigParameter.get_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_enabled", ""
        ).lower() in ["true", "1", "t", "y", "yes"]
        api_url = IrConfigParameter.get_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_api_url", ""
        )
        api_key = IrConfigParameter.get_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_api_key", ""
        )
        duration = int(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_duration", "210"
            )
        )
        delivery_duration = int(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_delivery_duration",
                "180",
            )
        )
        loading_duration = int(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_loading_duration",
                "45",
            )
        )
        resources_number = int(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_resources_number",
                "10",
            )
        )
        work_penalty = float(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_work_penalty", "9.0"
            )
        )
        travel_penalty = float(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_travel_penalty", "1.5"
            )
        )

        daily_work_time = float(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_daily_work_time",
                "10.0",
            )
        )

        return OptimizationConfig(
            enabled=enabled,
            api_url=api_url,
            api_key=api_key,
            duration=duration,
            delivery_duration=delivery_duration,
            loading_duration=loading_duration,
            resources_number=resources_number,
            work_penalty=work_penalty,
            travel_penalty=travel_penalty,
            daily_work_time=daily_work_time,
        )

    @api.model
    def default_get(self, fields):
        res = super(StockConfigSettings, self).default_get(fields)
        cfg = self.get_optimization_config()
        if "geo_optimization_enabled" in fields or not fields:
            res["geo_optimization_enabled"] = cfg.enabled
        if "geo_optimization_api_url" in fields or not fields:
            res["geo_optimization_api_url"] = cfg.api_url
        if "geo_optimization_api_key" in fields or not fields:
            res["geo_optimization_api_key"] = cfg.api_key
        if "geo_optimization_duration" in fields or not fields:
            res["geo_optimization_duration"] = cfg.duration
        if "geo_optimization_delivery_duration" in fields or not fields:
            res["geo_optimization_delivery_duration"] = cfg.delivery_duration
        if "geo_optimization_loading_duration" in fields or not fields:
            res["geo_optimization_loading_duration"] = cfg.loading_duration
        if "geo_optimization_resources_number" in fields or not fields:
            res["geo_optimization_resources_number"] = cfg.resources_number
        if "geo_optimization_work_penalty" in fields or not fields:
            res["geo_optimization_work_penalty"] = cfg.work_penalty
        if "geo_optimization_travel_penalty" in fields or not fields:
            res["geo_optimization_travel_penalty"] = cfg.travel_penalty
        if "geo_optimization_daily_work_time" in fields or not fields:
            res["geo_optimization_daily_work_time"] = cfg.daily_work_time

        return res

    @api.multi
    def set_geo_optimization_enabled(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_enabled",
            self.geo_optimization_enabled or "",
        )

    @api.multi
    def set_geo_optimization_api_url(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_api_url",
            self.geo_optimization_api_url or "",
        )

    @api.multi
    def set_geo_optimization_api_key(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_api_key",
            self.geo_optimization_api_key or "",
        )

    @api.multi
    def set_geo_optimization_duration(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_duration",
            self.geo_optimization_duration or "210",
        )

    @api.multi
    def set_geo_optimization_delivery_duration(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_delivery_duration",
            self.geo_optimization_delivery_duration or "180",
        )

    @api.multi
    def set_geo_optimization_loading_duration(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_loading_duration",
            self.geo_optimization_loading_duration or "45",
        )

    @api.multi
    def set_geo_optimization_resources_number(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_resources_number",
            self.geo_optimization_resources_number or "10",
        )

    @api.multi
    def set_geo_optimization_work_penalty(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_work_penalty",
            self.geo_optimization_work_penalty or "9",
        )

    @api.multi
    def set_geo_optimization_travel_penalty(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_travel_penalty",
            self.geo_optimization_travel_penalty or "1.5",
        )

    @api.multi
    def set_geo_optimization_daily_work_time(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_daily_work_time",
            self.geo_optimization_daily_work_time or "10.0",
        )
