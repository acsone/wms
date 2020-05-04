# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA, Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockConfigSettings(models.TransientModel):
    _inherit = "stock.config.settings"

    price_limit_for_inventory = fields.Float("Price limit for inventory")
    nbr_open_days = fields.Integer("Number of open days")
    months_between_inventory = fields.Integer(
        string="Number of months between two inventory for a product"
    )
    delay_inventory_expensive_products = fields.Integer(
        string="Delay between two inventory for expensive products",
        help="6 months means that it will be two inventory per year",
    )
    delay_inventory_best_sellers_products = fields.Integer(
        string="Delay between two inventory for best sellers products"
    )
    delay_inventory_other_products = fields.Integer(
        string="Delay between two inventory for other products"
    )
    best_sellers_duration = fields.Integer(
        string="Duration to compute best sellers (in months)"
    )
    best_sellers_percent = fields.Integer(
        string="Quantity to take for best sellers (in percent)"
    )

    @api.model
    def default_get(self, fields):
        res = super(StockConfigSettings, self).default_get(fields)

        config_param = self.env["ir.config_parameter"]
        if "price_limit_for_inventory" in fields or not fields:
            price = float(config_param.get_param("stock.price_limit_for_inventory", 0))
            res["price_limit_for_inventory"] = price
        if "nbr_open_days" in fields or not fields:
            days = int(config_param.get_param("stock.nbr_open_days", 0))
            res["nbr_open_days"] = days
        if "months_between_inventory" in fields or not fields:
            nbr_months = int(
                config_param.get_param("stock.months_between_inventory", 0)
            )
            res["months_between_inventory"] = nbr_months
        if "delay_inventory_expensive_products" in fields or not fields:
            nbr_months = int(
                config_param.get_param("stock.delay_inventory_expensive_products", 0)
            )
            res["delay_inventory_expensive_products"] = nbr_months
        if "delay_inventory_best_sellers_products" in fields or not fields:
            nbr_months = int(
                config_param.get_param("stock.delay_inventory_best_sellers_products", 0)
            )
            res["delay_inventory_best_sellers_products"] = nbr_months
        if "delay_inventory_other_products" in fields or not fields:
            nbr_months = int(
                config_param.get_param("stock.delay_inventory_other_products", 0)
            )
            res["delay_inventory_other_products"] = nbr_months
        if "best_sellers_duration" in fields or not fields:
            nbr_months = int(config_param.get_param("stock.best_sellers_duration", 0))
            res["best_sellers_duration"] = nbr_months
        if "best_sellers_percent" in fields or not fields:
            best_sellers_percent = int(
                config_param.get_param("stock.best_sellers_percent", 0)
            )
            res["best_sellers_percent"] = best_sellers_percent

        return res

    @api.multi
    def set_price_limit_for_inventory(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "stock.price_limit_for_inventory", self.price_limit_for_inventory or "0"
        )

    @api.multi
    def set_nbr_open_days(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "stock.nbr_open_days", self.nbr_open_days or "0"
        )

    @api.multi
    def set_months_between_inventory(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "stock.months_between_inventory", self.months_between_inventory or "0"
        )

    @api.multi
    def set_delay_inventory_expensive_products(self):
        self.ensure_one()

        self.check_delay(self.delay_inventory_expensive_products)
        self.env["ir.config_parameter"].set_param(
            "stock.delay_inventory_expensive_products",
            self.delay_inventory_expensive_products or "0",
        )

    @api.multi
    def set_delay_inventory_best_sellers_products(self):
        self.ensure_one()

        self.check_delay(self.delay_inventory_best_sellers_products)
        self.env["ir.config_parameter"].set_param(
            "stock.delay_inventory_best_sellers_products",
            self.delay_inventory_best_sellers_products or "0",
        )

    @api.multi
    def set_delay_inventory_other_products(self):
        self.ensure_one()

        self.check_delay(self.delay_inventory_other_products)
        self.env["ir.config_parameter"].set_param(
            "stock.delay_inventory_other_products",
            self.delay_inventory_other_products or "0",
        )

    @api.multi
    def set_best_sellers_duration(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "stock.best_sellers_duration", self.best_sellers_duration or "0"
        )

    @api.multi
    def set_best_sellers_percent(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "stock.best_sellers_percent", self.best_sellers_percent or "0"
        )

    @api.model
    def check_delay(self, delay):
        if not delay:
            return

        if delay > 12:
            raise UserError(_("The maximum delay is 12 months"))

        if delay not in [1, 2, 3, 4, 6, 12]:
            raise UserError(
                _(
                    "The delay can only be in the following list:\n"
                    "(1, 2, 3, 4, 6 or 12 months)"
                )
            )
