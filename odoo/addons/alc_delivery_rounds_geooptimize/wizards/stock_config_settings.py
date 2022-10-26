# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from collections import namedtuple

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import ormcache

OptimizationConfig = namedtuple(
    "OptimizationConfig",
    "enabled,api_url,api_key,duration,delivery_duration,loading_duration,"
    "resources_number,work_penalty,travel_penalty,daily_work_time,resource_cfg,"
    "method,delivery_window_start,delivery_window_end,delivery_window_disabled,"
    "options_cfg",
)


class StockConfigSettings(models.TransientModel):

    _inherit = "stock.config.settings"

    geo_optimization_enabled = fields.Boolean("Optimization activated")
    geo_optimization_api_url = fields.Char("TourSolver API url")
    geo_optimization_api_key = fields.Char("TourSolver API Key")
    geo_optimization_duration = fields.Integer(
        "Optimization process max duration",
        help="Duration in seconds allowed to the computation of the optimization",
    )
    geo_optimization_delivery_duration = fields.Integer(
        "Fixed time spent deliverying a customer",
        help="Duration in seconds needed to deliver a customer",
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

    geo_optimization_resource_cfg = fields.Text(
        "Additional resources configuration (json)"
    )
    geo_optimization_method = fields.Selection(
        selection=[
            ("fixed_sequence", "Fixed sequence computed from delivery windows"),
            ("fixed_itinerary", "Keep fixed round itinerary order"),
            ("optimized", "Computed by the geo optimisation mechanism"),
        ],
        default="fixed_sequence",
    )
    geo_optimization_dw_start = fields.Float("From", required=True, default=10.0)
    geo_optimization_dw_end = fields.Float("To", required=True, default=18.5)

    geo_optimization_dw_disabled = fields.Boolean(
        "Disable delivery windows", default=False
    )

    geo_optimization_options_cfg = fields.Text(
        "Additional options configuration (json)"
    )

    @api.constrains("geo_optimization_dw_start", "geo_optimization_dw_end")
    def check_window_no_onverlaps(self):
        for record in self:
            if record.geo_optimization_dw_start > record.geo_optimization_dw_end:
                DeliveryWindow = self.env["alc.delivery.window"]
                raise ValidationError(
                    _("%s must be > %s")
                    % (
                        DeliveryWindow.float_to_time_repr(
                            record.geo_optimization_dw_end
                        ),
                        DeliveryWindow.float_to_time_repr(
                            record.geo_optimization_dw_start
                        ),
                    )
                )

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
        resource_cfg = json.loads(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_resource_cfg", "{}"
            )
        )
        method = IrConfigParameter.get_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_method", "fixed_sequence",
        )

        geo_optimization_dw_start = float(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_dw_start", "10.0",
            )
        )
        geo_optimization_dw_end = float(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_dw_end", "18.5",
            )
        )
        delivery_window_disabled = IrConfigParameter.get_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_dw_disabled", ""
        ).lower() in ["true", "1", "t", "y", "yes"]

        options_cfg = json.loads(
            IrConfigParameter.get_param(
                "alc_delivery_rounds_geooptimize.geo_optimization_options_cfg", "{}"
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
            resource_cfg=resource_cfg,
            method=method,
            delivery_window_start=geo_optimization_dw_start,
            delivery_window_end=geo_optimization_dw_end,
            delivery_window_disabled=delivery_window_disabled,
            options_cfg=options_cfg,
        )

    @api.model  # noqa: C901
    def default_get(self, _fields):
        res = super(StockConfigSettings, self).default_get(_fields)
        cfg = self.get_optimization_config()
        if "geo_optimization_enabled" in _fields or not _fields:
            res["geo_optimization_enabled"] = cfg.enabled
        if "geo_optimization_api_url" in _fields or not _fields:
            res["geo_optimization_api_url"] = cfg.api_url
        if "geo_optimization_api_key" in _fields or not _fields:
            res["geo_optimization_api_key"] = cfg.api_key
        if "geo_optimization_duration" in _fields or not _fields:
            res["geo_optimization_duration"] = cfg.duration
        if "geo_optimization_delivery_duration" in _fields or not _fields:
            res["geo_optimization_delivery_duration"] = cfg.delivery_duration
        if "geo_optimization_loading_duration" in _fields or not _fields:
            res["geo_optimization_loading_duration"] = cfg.loading_duration
        if "geo_optimization_resources_number" in _fields or not _fields:
            res["geo_optimization_resources_number"] = cfg.resources_number
        if "geo_optimization_work_penalty" in _fields or not _fields:
            res["geo_optimization_work_penalty"] = cfg.work_penalty
        if "geo_optimization_travel_penalty" in _fields or not _fields:
            res["geo_optimization_travel_penalty"] = cfg.travel_penalty
        if "geo_optimization_daily_work_time" in _fields or not _fields:
            res["geo_optimization_daily_work_time"] = cfg.daily_work_time
        if "geo_optimization_resource_cfg" in _fields or not _fields:
            res["geo_optimization_resource_cfg"] = json.dumps(cfg.resource_cfg)
        if "geo_optimization_method" in _fields or not _fields:
            res["geo_optimization_method"] = cfg.method
        if "geo_optimization_dw_start" in _fields or not _fields:
            res["geo_optimization_dw_start"] = cfg.delivery_window_start
        if "geo_optimization_dw_end" in _fields or not _fields:
            res["geo_optimization_dw_end"] = cfg.delivery_window_end
        if "geo_optimization_dw_disabled" in _fields or not _fields:
            res["geo_optimization_dw_disabled"] = cfg.delivery_window_disabled
        if "geo_optimization_options_cfg" in _fields or not _fields:
            res["geo_optimization_options_cfg"] = json.dumps(cfg.options_cfg)

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

    @api.multi
    def set_geo_optimization_resource_cfg(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_resource_cfg",
            self.geo_optimization_resource_cfg or "{}",
        )

    @api.multi
    def set_geo_optimization_method(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_method",
            self.geo_optimization_method or "fixed_sequence",
        )

    @api.multi
    def set_geo_optimization_dw_start(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_dw_start",
            self.geo_optimization_dw_start or "10.0",
        )

    @api.multi
    def set_geo_optimization_dw_end(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_dw_end",
            self.geo_optimization_dw_end or "18.5",
        )

    @api.multi
    def set_get_delivery_window_disabled(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_dw_disabled",
            self.geo_optimization_dw_disabled or "",
        )

    @api.multi
    def set_geo_optimization_options_cfg(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_options_cfg",
            self.geo_optimization_options_cfg or "{}",
        )
